import os, json, re, datetime, sqlite3
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

DB_PATH = os.environ.get("SQLITE_DB_PATH", "sample.db")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MOCK_MODE = os.environ.get("MOCK_MODE", "0") == "1"

SQL_PLANNER_SYSTEM_PROMPT = os.environ.get("SQL_PLANNER_SYSTEM_PROMPT") or """
You are a data analyst assistant that answers questions using a SQLite database.

Rules:
1) Data scope: Only use the provided schema JSON. Do not invent tables/columns.
2) SQL dialect: SQLite. Use unqualified table names like events, orders.
3) Safety: SELECT-only; no DML/DDL. Use LIMIT 1000 unless aggregation makes fewer rows. Use COALESCE for nulls. Prefer named parameters like :start_date, :end_date, :limit.
4) Time filters: If timeframe is unspecified and data is time-based, default to last 30 days with parameters (:start_date, :end_date) using ISO date strings (YYYY-MM-DD).
5) Performance: Prefer aggregations over raw rows. Avoid SELECT *. Use WHERE filters.
6) Ambiguity: If the question is underspecified (metric, timeframe, entity), ask one concise clarifying question.
7) Output format: Return strict JSON only (no extra text).

Return ONLY JSON:
{
  "intent": "short description",
  "needs_clarification": true|false,
  "clarifying_question": "short question or null",
  "sql": "SELECT ...",
  "params": { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "limit": 1000 },
  "assumptions": ["defaults applied"],
  "confidence": 0.0-1.0
}
""".strip()

ANSWER_COMPOSER_SYSTEM_PROMPT = os.environ.get("ANSWER_COMPOSER_SYSTEM_PROMPT") or """
You summarize SQLite query results for business users.

Inputs:
- question, planner intent, assumptions
- sql (optional), params
- row_count, sample rows (<=50)

Write a concise answer:
- State the answer first with key figures and timeframe.
- Mention important filters/assumptions.
- If empty/low-confidence, say so and suggest one follow-up.
- Prefer a tiny table (<=10 rows) or bullets if helpful.
- No internal reasoning; user-facing content only.
""".strip()

if not OPENAI_API_KEY and not MOCK_MODE:
    raise RuntimeError("OPENAI_API_KEY is required (or set MOCK_MODE=1 for demo)")

oa_client = OpenAI(api_key=OPENAI_API_KEY) if not MOCK_MODE else None

# ---------- DB helpers ----------
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_sample_data(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_date TEXT,
            event_name TEXT,
            user_id TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_date TEXT,
            order_id TEXT PRIMARY KEY,
            user_id TEXT,
            amount_usd REAL,
            channel TEXT
        )
    """)
    cur.execute("SELECT COUNT(*) AS c FROM events")
    if cur.fetchone()[0] == 0:
        today = datetime.date.today()
        rows = [
            (str(today - datetime.timedelta(days=3)), "signup", "u1"),
            (str(today - datetime.timedelta(days=2)), "add_to_cart", "u1"),
            (str(today - datetime.timedelta(days=2)), "purchase", "u1"),
            (str(today - datetime.timedelta(days=10)), "signup", "u2"),
            (str(today - datetime.timedelta(days=1)), "signup", "u3"),
            (str(today - datetime.timedelta(days=1)), "add_to_cart", "u3"),
        ]
        cur.executemany("INSERT INTO events (event_date, event_name, user_id) VALUES (?, ?, ?)", rows)

    cur.execute("SELECT COUNT(*) AS c FROM orders")
    if cur.fetchone()[0] == 0:
        today = datetime.date.today()
        rows = [
            (str(today - datetime.timedelta(days=2)), "o1001", "u1", 120.50, "email"),
            (str(today - datetime.timedelta(days=7)), "o1002", "u2", 75.00, "paid_search"),
            (str(today - datetime.timedelta(days=1)), "o1003", "u3", 49.99, "social"),
        ]
        cur.executemany("INSERT INTO orders (order_date, order_id, user_id, amount_usd, channel) VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()

def get_schema_json(conn: sqlite3.Connection) -> Dict[str, Any]:
    schema = {"dialect": "sqlite", "tables": []}
    cur = conn.cursor()
    for tbl in ["events", "orders"]:
        cur.execute(f"PRAGMA table_info({tbl})")
        cols = [{"name": r[1], "type": r[2]} for r in cur.fetchall()]
        schema["tables"].append({"name": tbl, "columns": cols})
    return schema

# ---------- SQL validation ----------
DML_DDL_RE = re.compile(r";\s*(drop|insert|update|delete|create|alter|merge|truncate)\b", re.IGNORECASE)
SELECT_RE = re.compile(r"^\s*select\b", re.IGNORECASE)

def extract_tables(sql: str) -> List[str]:
    patterns = [r"\bfrom\s+([a-zA-Z_][\w_]*)", r"\bjoin\s+([a-zA-Z_][\w_]*)"]
    found: List[str] = []
    for pat in patterns:
        for m in re.finditer(pat, sql or "", re.IGNORECASE):
            found.append(m.group(1))
    return sorted(set(found))

def validate_sql(sql: str, allowed_tables: set):
    if not SELECT_RE.search(sql or ""):
        raise ValueError("Only SELECT queries are allowed")
    if DML_DDL_RE.search(sql or ""):
        raise ValueError("DML/DDL is forbidden")
    refs = extract_tables(sql)
    if not refs:
        raise ValueError("Query must reference at least one table")
    for ref in refs:
        if ref not in allowed_tables:
            raise ValueError(f"Table {ref} is not allowed")

# ---------- LLM calls ----------
def plan_sql(question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    if MOCK_MODE:
        q = (question or "").lower()
        start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        if "signup" in q:
            return {
                "intent": "count signups in last 30 days",
                "needs_clarification": False,
                "clarifying_question": None,
                "sql": "SELECT COUNT(*) AS signup_count FROM events WHERE event_name = 'signup' AND date(event_date) >= date(:start_date) LIMIT 1",
                "params": {"start_date": start_date, "limit": 1},
                "assumptions": ["defaulted to last 30 days"],
                "confidence": 0.9,
            }
        if "revenue" in q or "sales" in q:
            return {
                "intent": "sum revenue last 30 days",
                "needs_clarification": False,
                "clarifying_question": None,
                "sql": "SELECT COALESCE(SUM(amount_usd), 0) AS revenue_usd FROM orders WHERE date(order_date) >= date(:start_date) LIMIT 1",
                "params": {"start_date": start_date, "limit": 1},
                "assumptions": ["defaulted to last 30 days"],
                "confidence": 0.8,
            }
        if "orders by channel" in q or ("orders" in q and "channel" in q):
            return {
                "intent": "orders and revenue by channel last 30 days",
                "needs_clarification": False,
                "clarifying_question": None,
                "sql": "SELECT channel, COUNT(*) AS orders, COALESCE(SUM(amount_usd), 0) AS revenue_usd FROM orders WHERE date(order_date) >= date(:start_date) GROUP BY channel ORDER BY revenue_usd DESC LIMIT :limit",
                "params": {"start_date": start_date, "limit": 100},
                "assumptions": ["defaulted to last 30 days"],
                "confidence": 0.75,
            }
        return {
            "intent": "events breakdown last 30 days",
            "needs_clarification": False,
            "clarifying_question": None,
            "sql": "SELECT event_name, COUNT(*) AS event_count FROM events WHERE date(event_date) >= date(:start_date) GROUP BY event_name ORDER BY event_count DESC LIMIT :limit",
            "params": {"start_date": start_date, "limit": 100},
            "assumptions": ["defaulted to last 30 days"],
            "confidence": 0.6,
        }
    payload = {
        "question": question,
        "schema": schema,
        "now": datetime.datetime.utcnow().date().isoformat(),
    }
    resp = oa_client.chat.completions.create(
        model=os.environ.get("PLANNER_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SQL_PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)

def compose_answer(question: str, plan: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    if MOCK_MODE:
        intent = plan.get("intent", "")
        if not rows:
            return f"No results found for: {intent}. Consider refining the timeframe or filters."
        # Simple, readable summaries for common shapes
        if len(rows) == 1 and len(rows[0].keys()) == 1:
            k = list(rows[0].keys())[0]
            return f"{intent}: {rows[0][k]}"
        if len(rows) == 1:
            cols = rows[0]
            parts = [f"{k}={cols[k]}" for k in cols]
            return f"{intent}: " + ", ".join(parts)
        # Multiple rows -> show up to 5
        preview = rows[:5]
        return f"{intent} (showing {len(preview)} of {len(rows)} rows): " + json.dumps(preview)
    payload = {
        "question": question,
        "intent": plan.get("intent"),
        "assumptions": plan.get("assumptions", []),
        "sql": plan.get("sql"),
        "params": plan.get("params", {}),
        "row_count": len(rows),
        "rows": rows[:50],
    }
    resp = oa_client.chat.completions.create(
        model=os.environ.get("COMPOSER_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": ANSWER_COMPOSER_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content

# ---------- FastAPI ----------
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    text: Optional[str] = None
    sql: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    followUp: Optional[str] = None

app = FastAPI(title="SQLite Chatbot", version="1.0")

conn = get_conn()
init_sample_data(conn)
SCHEMA_JSON = get_schema_json(conn)
ALLOWED_TABLES = {t["name"] for t in SCHEMA_JSON["tables"]}

@app.get("/health")
def health():
    return {"status": "ok", "db": os.path.abspath(DB_PATH), "tables": sorted(ALLOWED_TABLES)}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        plan = plan_sql(req.question, SCHEMA_JSON)

        if plan.get("needs_clarification") and plan.get("clarifying_question"):
            best_sql = plan.get("sql")
            params = plan.get("params", {}) or {}
            if best_sql:
                validate_sql(best_sql, ALLOWED_TABLES)
                return ChatResponse(followUp=plan["clarifying_question"], sql=best_sql, params=params)
            return ChatResponse(followUp=plan["clarifying_question"])

        sql = plan.get("sql")
        params = plan.get("params", {}) or {}
        if not sql:
            raise ValueError("Planner did not return SQL")

        validate_sql(sql, ALLOWED_TABLES)

        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        text = compose_answer(req.question, plan, rows)
        return ChatResponse(text=text, sql=sql, params=params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

