from pymongo import MongoClient
import csv
db = MongoClient()["tagRecommender"]["data_200000"]
with open('temp.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile)
	for row in spamreader:
		print(row[0])	
		obj = {
		"_id" : row[1].replace(".",""),
		"title" : row[1],
		"body" : row[2],
		"tags" : row[3]
		}
		db.update({"_id" : obj["_id"]},obj,True)

