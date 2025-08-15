from fastapi import FastAPI
from pydantic import BaseModel,EmailStr,constr


app = FastAPI()

class datavalidation(BaseModel):
        a:int
        b:int

@app.get("/")
def multiple(a: int, b: int):
    return {"result": a * b}

#   uvicorn FirstAPI:app --reload
