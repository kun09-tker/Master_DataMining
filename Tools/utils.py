import json

def update_class_courses():
    with open('Lib/class_course.json', 'r', encoding='utf-8') as file:
        course_mapping = json.load(file)