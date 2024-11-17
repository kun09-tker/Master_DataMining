import json
import numpy as np
from Tools import *

def predict_outcome(predict_course_name, pass_courses, gender):
    classes = get_classes()
    class_of_predict_course = class_of_course(classes, predict_course_name)
    if class_of_predict_course == None:
        return "NoEvent", "Unknow", "NotFoundClass"
    pass_courses = insert_or_update([], pass_courses)
    print(pass_courses)
    pass_courses_using_predict = [course for course in pass_courses
                                  if class_of_course(classes, course.name) == class_of_predict_course and class_of_predict_course != None]
    checker = check_studied(predict_course_name, pass_courses_using_predict)
    if checker:
        return "Studied", checker, translate(class_of_predict_course)
        
    if not pass_courses_using_predict:
        return "NoInfo", "Border", translate(class_of_predict_course)
    result = predict_base_class(class_of_predict_course, pass_courses_using_predict, gender)
    return result

def get_classes():
    with open('Lib/class_course.json', 'r', encoding='utf-8') as file:
        return json.load(file) 

def class_of_course(classes, course_name):
    for class_name in classes.keys():
        if course_name in classes[class_name]["CoursesName"]:
            return class_name
    return None

def predict_base_class(class_name, pass_courses, gender):
    try:
        centroids = np.load(f'Lib/Centroids/{class_name}_centroid.npy')
        distances = [euclidean_distance(extract_feature(centroids, gender), centroid, axis=0) for centroid in centroids]
        return "NoEvent", outcome_mapping(np.argmin(distances)), translate(class_name)
    except Exception as e:
        return "MissCluster", "Unknow", translate(class_name)

def extract_feature(courses, gender):
    return np.random.rand(courses.shape[1]) * 10.0

def outcome_mapping(index):
    mapping = ["Pass", "Border", "Fail"]
    return mapping[index]

def translate(code):
    mapping = {
        "FoundationCourses": "Các học phần cơ sở ngành CNTT",
        "GeneralCourses": "Các học phần chung",
        "MajorCourses": "Các học phần chuyên ngành CNTT",
        "GraduationCourses": "Các học phần tốt nghiệp/thực tập"
    }
    return mapping[code]

def check_studied(pre_name, pass_course):
   course_studied = [course for course in pass_course if course.name == pre_name]
   if course_studied:
       course_studied = course_studied[0]
       GPA = 0.4 * course_studied.midtermScore + 0.6 * course_studied.finalScore
       if GPA < 4.0:
           return "Fail"
       else:
           return "Pass"
   return None

def insert_or_update(data_list, data):
    for new_entry in data:
        if not data_list:
            data_list.append(new_entry)
            continue
        
        updated = False
        
        for idx, item in enumerate(data_list):
            if item.name == new_entry.name:
                data_list[idx] = item.copy(update={
                        "midtermScore": new_entry.midtermScore,
                        "finalScore": new_entry.finalScore
                    })
                updated = True
        
        if not updated:
            data_list.append(new_entry)
    
    return data_list
