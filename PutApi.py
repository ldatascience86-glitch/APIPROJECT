
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

user_db ={
    1: {"name":"Prabhakar","Age" : 40},
    2: {"name":"Rajeev","Age" : 39},
    3: {"name":"manish","Age" : 45}
}
class User(BaseModel):
    name : str
    Age : int 

@app.put("/update/Vi/{user_id}")
def user_upate(user_id :int, user:User):
    if user_id in user_db:
        user_db[user_id] = user.dict()
       # print(user_db)
        return  {
           "Message" :"user is updated successfully ","User ":user_db[user_id]
        }
    else:
        return{
           "Message" :"user is has not been updated successfully ","User ":user_db[user_id]
        }
@app.delete("/delete/Vi/{user_id}")   
def user_delete(user_id :int):
    if user_id in user_db:
        del user_db[user_id]
        return {
            "Message" : "User delete successfully"
        }    
    else: 
        return{
            "Message" : "User not found"
    }
