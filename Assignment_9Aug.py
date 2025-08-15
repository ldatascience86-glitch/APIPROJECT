from fastapi import FastAPI
from pydantic import BaseModel,EmailStr,constr
#import requests
app = FastAPI()
# In-memory "database"
users_db = []

class Userregistraion(BaseModel):
    UserName:str
    Email:EmailStr #auto validate the email
    password :constr(min_length=8)

@app.post("/")

def Register_User(user:Userregistraion):
    users_db.append({
            "Username" : user.UserName,
            "Email" : user.Email,
            "password" : user.password,
        })
    return {
        "message": "Registration successful!",
        "username": user.UserName,
        "email": user.Email
    }
@app.get("/user")
def get_user():
    return [
        {key: value for key, value in user.items() }
        for user in users_db
    ]
