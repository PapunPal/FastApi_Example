from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI()

# --------------------------------
# 1. Python Data Structure
# --------------------------------

students = [
    {
        "id": 1,
        "name": "Rahul",
        "age": 25,
        "course": "Java",
        "city": "Pune"
    },
    {
        "id": 2,
        "name": "Amit",
        "age": 28,
        "course": "Python",
        "city": "Mumbai"
    },
    {
        "id": 3,
        "name": "Priya",
        "age": 24,
        "course": "Java",
        "city": "Hyd"
    }
]

# --------------------------------
# 2. Pydantic Model
# --------------------------------

class Student(BaseModel):
    name: str
    age: int
    course: str
    city: str

# --------------------------------
# 3. CREATE - POST
# --------------------------------

@app.post("/students")
def create_student(student: Student):

    new_student = {
        "id": max([s["id"] for s in students], default=0) + 1,
        "name": student.name,
        "age": student.age,
        "course": student.course,
        "city": student.city
    }

    students.append(new_student)

    return {
        "message": "Student created successfully",
        "data": new_student
    }


# --------------------------------
# 4. READ ALL - GET
# --------------------------------

@app.get("/students")
def get_students(course: str = None, city: str = None):

    result = students

    if course:
        result = [
            s for s in result
            if s["course"].lower() == course.lower()
        ]

    if city:
        result = [
            s for s in result
            if s["city"].lower() == city.lower()
        ]

    return {
        "total": len(result),
        "data": result
    }


@app.get("/students/{student_id}")
def get_student(student_id: int):

    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )

@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):

    for index, existing_student in enumerate(students):

        if existing_student["id"] == student_id:

            updated_student = {
                "id": student_id,
                "name": student.name,
                "age": student.age,
                "course": student.course,
                "city": student.city
            }

            students[index] = updated_student

            return {
                "message": "Student updated successfully",
                "data": updated_student
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )

@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    for index, student in enumerate(students):

        if student["id"] == student_id:

            deleted_student = students.pop(index)

            return {
                "message": "Student deleted successfully",
                "data": deleted_student
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )
