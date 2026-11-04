from fastapi import FastAPI
from pydantic import BaseModel


# Create FastAPI application

app = FastAPI()

# Define GET API

@app.get("/")

def home():

    return {"message": "Welcome Papun "}

@app.get("/student")
def student():
    return{
        'id':1000,
        "name":"papun",
        "course":"python"
    }


@app.get("/students/{student_id}")
def get_student(student_id: int):

    return {"student_id": student_id}



@app.get("/search")
def search_students(course: str, city: str):
    return {
        "course": course,
        "city": city
    }

class Students(BaseModel):
    id:int
    name:str
    course:str
    city:str


@app.post("/students")
def create_student(student:Students):
    return student

