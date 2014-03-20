from pymongo import MongoClient
import sys
db =  MongoClient()["tagRecommender"]["data_200000"]
#tags = []
tags = {}
count = 0

db2 =  MongoClient()["tagRecommender"]["insgats"]
for each in db2.find({"name": "ankit"}):
	for t in each["tags"].keys():
		print(t  +  "," + str(each["tags"][t]) )
sys.exit(0)
for each in db.find():
	
	count = count + 1 
	print(count)
	tag = each["tags"].split()
	for t in tag:
		key = t.replace(".","@@@")
		if key not in tags.keys():
			tags[key] = 0
		tags[key] = tags[key] + 1
	#if tag[0] not in tags:
#		print(tag[0])
#		tags.append(tag[0])
	#for eachtag in tag:
#		if eachtag not in tags:
#			print(eachtag)
#			tags.append(eachtag)

db2 =  MongoClient()["tagRecommender"]["insgats"]
obj = {
	"tags" :  tags
}
db2.insert(obj)

#for each in tags.keys():
#	print()