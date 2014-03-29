from pymongo import MongoClient
db =  MongoClient()["semantified"]["terms"]

for each in db.find():
	print(each["term"] +  ","+str(each["hasDisam"]))