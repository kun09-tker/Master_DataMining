import json
import numpy as np
from Tools import *
from scipy.stats import gmean

def predict_outcome(predict_course_name, pass_courses):
    classes = get_classes()
    class_of_predict_course = class_of_course(classes, predict_course_name)

    if class_of_predict_course == None:
        return "NoEvent", "Unknown", "NotFoundClass"
    
    rank = get_rank(class_of_predict_course)
    
    pass_courses = insert_or_update([], pass_courses)
    if len(pass_courses) < 3:
        return "NotEnough", "Unknown", translate(class_of_predict_course)
    
    pass_courses_using_predict = [course for course in pass_courses
                                  if class_of_course(classes, course.name) == class_of_predict_course and class_of_predict_course != None]
    checker = check_studied(predict_course_name, pass_courses_using_predict)
    if checker:
        return "Studied", checker, translate(class_of_predict_course)
    
    print(len(pass_courses_using_predict))

    if len(pass_courses_using_predict) < 3:
        r = rank[predict_course_name]
        grade = "Fail"
        if r == rank[max(rank, key=rank.get)]:
            grade = "Pass"
        return "NoEvent", grade, translate(class_of_predict_course)
    result = predict_base_class(class_of_predict_course, pass_courses_using_predict,
                                predict_course_name, rank)
    return result

def get_classes():
    with open('Lib/class_course.json', 'r', encoding='utf-8') as file:
        return json.load(file)
    
def get_rank(class_course):
    with open(f'Lib/Ranking/{class_course}_ranking.json', 'r', encoding='utf-8') as file:
        return json.load(file)
def get_credits():
    with open(f'Lib/credits.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def class_of_course(classes, course_name):
    for class_name in classes.keys():
        if course_name in classes[class_name]["CoursesName"]:
            return class_name
    return None

def predict_base_class(class_name, pass_courses_using_predict,
                       predict_course_name, rank):
    try:
        centroids = np.load(f'Lib/Centroids/{class_name}_k_means.npy')
        point = extract_feature(pass_courses_using_predict, predict_course_name, rank)
        distances = [euclidean_distance(point, centroid, axis=0) for centroid in centroids]
        print(distances)
        return "NoEvent", outcome_mapping(class_name, np.argmin(distances)), translate(class_name)
    except Exception as e:
        print(e)
        return "Miss", "Unknown", translate(class_name)

def extract_feature(pass_courses_using_predict, predict_course_name, rank):
    overcome = np.array(
        [rank[c.name] for c in pass_courses_using_predict] + [rank[predict_course_name]],
    dtype=np.float64).mean()

    midterm_scores = np.array([c.midtermScore for c in pass_courses_using_predict], dtype=np.float64)
    midterm_scores[midterm_scores == 0] = 1
    final_scores = np.array([c.finalScore for c in pass_courses_using_predict], dtype=np.float64)
    final_scores[final_scores == 0] = 1

    return [overcome, gmean(midterm_scores), gmean(final_scores)]

def outcome_mapping(class_name, index):
    with open('Lib/grade.json', 'r', encoding='utf-8') as file:
        mapping = json.load(file)
    return mapping[class_name][index]

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
