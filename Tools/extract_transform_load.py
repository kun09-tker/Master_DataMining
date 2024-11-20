import json
import numpy as np
import pandas as pd
from Connection.database import *
from scipy.stats import gmean

class ExtractTransformLoad:
    def __init__(self) -> None:
        self.df = None
        self.feature = {}
        self.miss_course_name = []
        self.database = Database()
        with open('Lib/class_course.json', 'r', encoding='utf-8') as file:
            self.course_mapping = json.load(file) 

    def extract_data(self, file_name):
        self.df = pd.read_excel(f"Data/{file_name}.xlsx")
    
    def transform_data(self):
        self.df.columns = self.df.columns.str.replace(r"M.*SV", "Index", regex=True)
        self.df.columns = self.df.columns.str.replace(r"T.*n h.*c ph.*n", "CourseName", regex=True)
        self.df.columns = self.df.columns.str.replace(r".*i.*m gi.* k.*", "MidTermScore", regex=True)
        self.df.columns = self.df.columns.str.replace(r".*i.*m cu.* k.*", "FinalScore", regex=True)
        self.df.columns = self.df.columns.str.replace(r"S.*TC", "Credits", regex=True)
        self.df.columns = self.df.columns.str.replace(r"Gi.*t.*nh", "Gender", regex=True)
        
        df = self.df

        df["GPA"] = 0.4 * df["MidTermScore"] + 0.6 * df["FinalScore"]
        df["MidTermScore"] = df["MidTermScore"].replace(0, 1)
        df["FinalScore"] = df["FinalScore"].replace(0, 1)
        df["CourseClass"] = self.course_class()
        df = df[df["CourseClass"] != "Unknows"]
        self.save_credits()

        classes_name = df["CourseClass"].unique()
        for cname in classes_name:
            df_cname = df[df["CourseClass"] == cname]
            df_cname = df_cname.drop(columns=["CourseClass"])
            df_cname["Rank"] = self.get_rank(df_cname)
            self.save_ranking(cname, df_cname)
            df_cname = df_cname.drop(columns=["CourseName"])

            group_index = df_cname.groupby(["Index", "Gender"])
            [index, gender] = self.get_index_from_group(group_index)
            overcome = group_index["Rank"].mean().values
            mid_term_score = group_index["MidTermScore"].apply(lambda x: gmean(x)).fillna(0).values
            final_score = group_index["FinalScore"].apply(lambda x: gmean(x)).fillna(0).values
            
            self.feature[cname] = pd.DataFrame({
                "Index": index,
                "Overcome": overcome,
                "MidTermScore": mid_term_score,
                "FinalScore": final_score 
            })
    
    def load_data(self):
        self.miss_course_name = list(set(self.miss_course_name))
        df_info = pd.DataFrame({
            "MissCourse":  [self.miss_course_name],
            "TotalOfStudent": len(self.df["Index"].unique()),
            "TotalOfCourses": len(self.df["CourseName"].unique())
        })
        df_info.to_json(f"Data/Info.json", orient="records", force_ascii=False, indent=4)
        for cname in self.feature.keys():
            self.database.update_or_insert(self.feature[cname], cname)

    def __call__(self, file_name):
        self.extract_data(file_name)
        self.transform_data()
        self.load_data()
        return self.miss_course_name

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
        df_fail = df[df['GPA'] < 4.0][['CourseName', 'GPA']]
        course_counts = df_fail['CourseName'].value_counts()
        course_order = course_counts.index.to_numpy()
        max_rank = len(course_order) + 1
        rank_mapping = {course: rank + 1 for rank, course in enumerate(course_order)}
        for course in total_courses:
            if course not in rank_mapping.keys():
                rank_mapping[course] = max_rank
        return df['CourseName'].map(rank_mapping).values

    def save_ranking(self, class_name, df):
        df = df[["CourseName", "Rank"]].drop_duplicates()
        result = dict(zip(df["CourseName"], df["Rank"]))
        with open(f'Lib/Ranking/{class_name}_ranking.json', 'w', encoding='utf-8') as rank:
            json.dump(result, rank, ensure_ascii=False, indent=4)
    
    def save_credits(self):
        df = self.df[["CourseName", "Credits"]].drop_duplicates()
        result = dict(zip(df["CourseName"], df["Credits"]))
        with open('Lib/credits.json', 'w', encoding='utf-8') as c:
            json.dump(result, c, ensure_ascii=False, indent=4)

