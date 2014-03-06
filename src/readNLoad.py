from pymongo import MongoClient
import csv
db = MongoClient()["tagRecommender"]["data"]
with open('newvaluemy1000.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile)
	for row in spamreader:
		print(row[0])	
		obj = {
		"title" : row[1],
		"body" : row[2],
		"tags" : row[3]
		}
		db.insert(obj)

