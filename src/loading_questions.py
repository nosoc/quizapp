import pandas
from pymongo import MongoClient

DATABASE_NAME = "summertime_webness"

questions = pandas.read_csv("C:/Users/1/Desktop/quiz_questions.csv", sep=";", encoding="windows-1251")

questions_dict = []

for index, row in questions.iterrows():
    d = {'question': row["lyrics"],
         'answers': {'a': row["artist_true"], 'b': row["artist_false_1"],
         'c': row["artist_false_2"], 'd': row["artist_false_3"]}, 'correct_answer': 'a'}
    questions_dict.append(d)

db = MongoClient('wardoctor.nosoc.io', port=443)[DATABASE_NAME]
for q in questions_dict:
    db['questions'].insert(q)
