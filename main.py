import os
import uvicorn
import requests
from Core import *
from Tools import *
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    predict_course = data.predictCourse
    pass_courses = data.passCourses
    message = None
    event, result, class_course = predict_outcome(predict_course, pass_courses)

    if event == "NoInfo":
        message = f"""Lưu ý, {predict_course} thuộc loại môn học {class_course}. Thông tin bạn cung cấp không có môn nào thuộc {class_course}. Kết quả dự đoán này chỉ dựa trên tình hình chung."""
    elif event == "Miss":
        message = f"""Lưu ý, vui lòng kiểm tra thông tin đầu vào hoặc hệ thống chưa có thông tin để dựa đoán mô học này."""
    elif event == "Studied":
        message = f"""Xin lỗi, bạn không cần dự đoán học phần này vì bạn đã học học phần này rồi. Kết quả là {result}"""
    elif event == "NotEnough":
        message = f"""Xin lỗi, bạn không cần nhập ít nhất 3 kết quả học phần khác nhau"""
    elif result == "Unknown":
        message = """Xin lỗi, hệ thống không tìm thấy thông tin của học phần bạn muốn dự đoán."""
    
    if message:
        return {"result": result, "message": message}
    return {"result": result}

class Login(BaseModel):
    username: str
    password: str


@app.post("/login/")
async def login(login: Login):
    load_dotenv()
    print(os.getenv("USERNAME_ADMIN"))
    print(os.getenv("PASSWORD_ADMIN"))
    if login.username == os.getenv("USERNAME_ADMIN") and login.password == os.getenv(
        "PASSWORD_ADMIN"
    ):
        return {"status": 200}
    return {"status": 401}


class URL(BaseModel):
    url: str

@app.post("/upload/")
async def upload(url: URL):
    ETL = ExtractTransformLoad()
    try:
        file_id = url.url.split("/d/")[1].split("/")[0]
    except IndexError:
        return {
            "status": "False"
        }
    output_file = "Data/Ksample.xlsx"
    try:
        # Send GET request
        download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Write the file to disk
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        miss_course = ETL("Ksample")
        if miss_course:
            return {
                "status": "Update",
                "info":{
                    "course": miss_course,
                    "type": [
                        "Các học phần chung",
                        "Các học phần cơ sở ngành CNTT",
                        "Các học phần chuyên ngành CNTT",
                        "Các học phần tốt nghiệp/thực tập"
                    ]
                }
            }
        return {
            "status": "True"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "False"
        }   

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
