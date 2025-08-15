from fastapi import FastAPI, HTTPException, Body
from pydantic import EmailStr, constr

app = FastAPI()

@app.post("/")
def Register_User(
    UserName: str = Body(...),
    Email: EmailStr = Body(...),  # EmailStr still works for validation
    password: constr(min_length=8) = Body(...)  # min length validation
):
    # Example logic for saving or processing
    return {
        "message": "Registration successful!",
        "username": UserName,
        "email": Email
    }
