from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, SessionLocal

# Database mein tables create karna
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Database connection dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Data validation schema
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    course: str

# 1. Frontend Webpage Serve karna
@app.get("/portal")
def serve_frontend():
    return FileResponse("index.html")

# 2. Welcome Route
@app.get("/")
def read_root():
    return {"message": "Welcome to Academic Analytics API by Abhitosh Anand"}

# 3. CREATE: Naya student add karna (POST)
@app.post("/students/")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(first_name=student.first_name, last_name=student.last_name, course=student.course)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# 4. READ: Saare students ka data lana (GET)
@app.get("/students/")
def read_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students

# 5. DELETE: Student ko delete karna (DELETE)
@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
        return {"message": "Student deleted successfully"}
    return {"error": "Student not found"}

# 6. UPDATE: Existing student ka data change karna (PUT)
@app.put("/students/{student_id}")
def update_student(student_id: int, student_data: StudentCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        student.first_name = student_data.first_name
        student.last_name = student_data.last_name
        student.course = student_data.course
        db.commit()
        db.refresh(student)
        return student
    return {"error": "Student not found"}