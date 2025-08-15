from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

class CalculationRequest(BaseModel):
    number1 :float
    number2 : float
    operation : str

@app.post("/calculate")
def calculate(data: CalculationRequest):
    op = data.operation.lower()
    
    if op == "add":
        result = data.number1 + data.number2
    elif op == "subtract":
        result = data.number1 - data.number2
    elif op == "multiply":
        result = data.number1 * data.number2
    elif op == "divide":
        if data.number2 == 0:
            raise HTTPException(status_code=400, detail="Division by zero is not allowed")
        result = data.number1 / data.number2
    else:
        raise HTTPException(status_code=400, detail="Invalid operation type. Use add, subtract, multiply, divide.")
    
    return {
        "number1": data.number1,
        "number2": data.number2,
        "operation": op,
        "result": result
    }