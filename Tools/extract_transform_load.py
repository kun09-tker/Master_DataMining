import json
import numpy as np
import pandas as pd
from Connection.mongo_db import *

class ExtractTransformLoad:
    def __init__(self) -> None:
        self.df = None
        self.feature = {}
        self.miss_course_name = []
        self.database = MongoDB()
        with open('Lib/class_course.json', 'r', encoding='utf-8') as file:
            self.course_mapping = json.load(file) 

    def extract_data(self, file_name):
        self.df = pd.read_excel(f"Data/{file_name}.xlsx")
    
    def transform_data(self):
        df = self.df.drop(columns=[
            "Họ và tên",
            "Ngày sinh",
            "Nơi sinh",
            "Lớp",
            "Năm học",
            "Học kỳ",
            "Điểm trung binh thang điểm 10",
            "Tổng kết chữ",
            "Đạt"])
        df = df.rename(columns={
            "Mã SV": "Index",
            "Tên học phần": "CourseName",
            "Điểm giữa kỳ": "MidTermScore",
            "Điểm cuối kỳ": "FinalScore",
            "Giới tính": "Gender",
            "Số TC": "Credits"})

        self.df = df

        df["GPA"] = 0.4 * df["MidTermScore"] + 0.6 * df["FinalScore"]
        df["RadioFinalAndMid"] = (df["FinalScore"] / df["MidTermScore"]).replace(np.inf, 0)
        df["Gender"] = df["Gender"].map({
            True: 0,
            False: 1
        })
        df["CourseClass"] = self.course_class()
        
        df = df[df["CourseClass"] != "Unknows"]
        
        classes_name = df["CourseClass"].unique()
        # print(classes_name)
        for cname in classes_name:
            df_cname = df[df["CourseClass"] == cname]
            df_cname = df_cname.drop(columns=["CourseClass"])
            df_cname["Rank"] = self.get_rank(df_cname)
            df_cname = df_cname.drop(columns=["CourseName"])

            group_index = df_cname.groupby(["Index", "Gender"])
            [index, gender] = self.get_index_from_group(group_index)
            number_of_credits = group_index["Credits"].sum().values
            overcome = group_index["Rank"].mean().values
            total_GPA = group_index["GPA"].sum().values
            seriousness = group_index["RadioFinalAndMid"].mean().values

            self.feature[cname] = pd.DataFrame({
                "Index": index,
                "Gender" : gender,
                "Overcome": overcome,
                "Accumulation": total_GPA / number_of_credits,
                "Seriousness": seriousness
            })
    
    def load_data(self):
        self.miss_course_name = list(set(self.miss_course_name))
        for cname in self.feature.keys():
            self.database.update_or_insert(self.feature[cname], cname)

    def etl_pipeline(self, file_name):
        self.extract_data(file_name)
        self.transform_data()
        self.load_data()

    def course_class(self):
        return [self.which_class(course_name)
                for course_name in self.df["CourseName"]]
    
    def which_class(self, course_name):
        for class_name in self.course_mapping.keys():
            if course_name in self.course_mapping[class_name]["CoursesName"]:
                return class_name
        self.miss_course_name.append(course_name)
        return "Unknows"

    def get_index_from_group(self, group):
        group_keys = list(group.groups.keys())
        group_keys_list = [list(item) for item in group_keys]
        return list(map(list, zip(*group_keys_list)))

    def get_rank(self, df):
        total_courses = df['CourseName'].unique()
        df_fail = df[df['GPA'] < 5.0][['CourseName', 'GPA']]
        course_counts = df_fail['CourseName'].value_counts()
        course_order = course_counts.index.to_numpy()
        max_rank = len(course_order) + 1
        rank_mapping = {course: rank + 1 for rank, course in enumerate(course_order)}
        for course in total_courses:
            if course not in rank_mapping.keys():
                rank_mapping[course] = max_rank
        return df['CourseName'].map(rank_mapping).values

