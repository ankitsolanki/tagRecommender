from pymongo import MongoClient
statdb = MongoClient()["tagRecommender"]["stats"]

for each in statdb.find({"_id" : "intialStats-10"}):
	for e in each["statsBigram"].keys():
		if each["statsBigram"][e] > 1 :
			print(e + "," +str(each["statsBigram"][e]))
