import os
import uvicorn
from Core import *
from typing import List
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel

app = FastAPI()

class InfoStudent(BaseModel):
    name: str
    idStudent: str
    dateBirth: str
    gender: str

class passCourse(BaseModel):
    name: str
    midtermScore: int
    finalScore: int

class Data(BaseModel):
    infoStudent: InfoStudent
    predictCourse: str
    passCourses: List[passCourse] = []

@app.post("/predict/")
async def predict(data: Data):
    print(data)
    info_student = data.infoStudent
    predict_course = data.predictCourse
    pass_courses = data.passCourses
    gender = info_student.gender
    message = ""
    event, result, class_course = predict_outcome(predict_course, pass_courses, gender)

    if event == "NoInfo":
        message = f'''Lưu ý, {predict_course} thuộc loại môn học {class_course}. Thông tin bạn cung cấp không có môn nào thuộc {class_course}. Kết quả dự đoán này chỉ dựa trên tình hình chung.'''
    elif event == "MissCluster":
        message = f'''Lưu ý, học phần {predict_course} thuộc loại môn học {class_course}, tuy nhiên hệ thống chưa có thông tin để dựa đoán mô học này.'''
    elif event == "Studied":
        message = f'''Xin lỗi, bạn không cần dự đoán học phần này vì bạn đã học học phần này rồi. Kết quả là {result}'''
    elif result == "Unknow":
        message = '''Xin lỗi, hệ thống không tìm thấy thông tin của học phần bạn muốn dự đoán.'''
    
    return {
        "result": result,
        "message": message
    }

class Login(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(login: Login):
    load_dotenv()
    print(os.getenv("USERNAME_ADMIN"))
    print(os.getenv("PASSWORD_ADMIN"))
    if login.username == os.getenv("USERNAME_ADMIN") and login.password == os.getenv("PASSWORD_ADMIN"):
        return {
            "status": 200
        }
    return {
        "status": 401
    }

class URL:
    url: str

# @app.post("/upload/")
# async def upload(url: URL):

    

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
