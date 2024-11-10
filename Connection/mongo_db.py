import os
from dotenv import load_dotenv
from pymongo import MongoClient
class MongoDB():
    def __init__(self) -> None:
        load_dotenv()
        username = os.getenv("USERNAME_MONGO_DB")
        password = os.getenv("PASSWORD_MONGO_DB")
        my_database = os.getenv("DATABASE_NAME")
        client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.wb0ti.mongodb.net/")
        self.db = client[my_database]
    
    def update_or_insert(self, df, class_course_name):
        datas = df.to_dict(orient="records")
        collection = self.db[class_course_name]
        for data in datas:
            print(data)
            collection.update_one({
                "$and": [
                    {"Index": data["Index"]},
                    {"Gender": data["Gender"]},
                    {"Overcome": data["Overcome"]},
                    {"Accumulation": data["Accumulation"]},
                    {"Seriousness": data["Seriousness"]}
                ]},
                {"$set": data},
                upsert=True
            )
