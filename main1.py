
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Dict

# 1. Create FastAPI application
app = FastAPI(
    title="Employee Management API",
    description="A REST API for managing employee records",
    version="1.0.0"
)

# 2. In-memory employee storage
employees: Dict[int, dict] = {
    1: {
        "id": 1,
        "name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "department": "IT",
        "salary": 50000
    },
    2: {
        "id": 2,
        "name": "Priya Singh",
        "email": "priya@gmail.com",
        "department": "HR",
        "salary": 45000
    }
}

# 3. Pydantic model for request validation
class Employee(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    department: str
    salary: float = Field(gt=0)


# 4. Global handler for unexpected exceptions
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "detail": "An unexpected error occurred."
        }
    )


# 5. Global handler for invalid request data
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Error",
            "errors": exc.errors()
        }
    )


# 6. CREATE - Add a new employee
@app.post("/employees", status_code=201)
def create_employee(employee: Employee):

    # Check whether email already exists
    for emp in employees.values():
        if emp["email"] == employee.email:
            raise HTTPException(
                status_code=409,
                detail="Employee email already exists"
            )

    new_id = max(employees.keys(), default=0) + 1

    new_employee = {
        "id": new_id,
        **employee.model_dump()
    }

    employees[new_id] = new_employee

    return {
        "success": True,
        "message": "Employee created successfully",
        "data": new_employee
    }


# 7. READ - Get all employees
@app.get("/employees")
def get_all_employees():

    return {
        "success": True,
        "total": len(employees),
        "data": list(employees.values())
    }


# 8. READ - Get employee by ID
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):

    if employee_id not in employees:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "success": True,
        "data": employees[employee_id]
    }


# 9. UPDATE - Update an existing employee
@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee: Employee
):

    if employee_id not in employees:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Prevent duplicate email for another employee
    for emp_id, emp in employees.items():
        if emp["email"] == employee.email and emp_id != employee_id:
            raise HTTPException(
                status_code=409,
                detail="Email already belongs to another employee"
            )

    updated_employee = {
        "id": employee_id,
        **employee.model_dump()
    }

    employees[employee_id] = updated_employee

    return {
        "success": True,
        "message": "Employee updated successfully",
        "data": updated_employee
    }


# 10. DELETE - Delete an employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):

    if employee_id not in employees:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    deleted_employee = employees.pop(employee_id)

    return {
        "success": True,
        "message": "Employee deleted successfully",
        "data": deleted_employee
    }


# 11. Root endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Employee Management API"
    }

@app.get("/test-error")
def test_error():

    result = 10 / 0

    return {"result": result}    
