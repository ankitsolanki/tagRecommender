from pymongo import MongoClient

db =  MongoClient()["tagRecommender"]["data_200000"]
tags = []
for each in db.find():
	tag = each["tags"].split()
	if tag[0] not in tags:
		print(tag[0])
		tags.append(tag[0])
	#for eachtag in tag:
#		if eachtag not in tags:
#			print(eachtag)
#			tags.append(eachtag)

db2 =  MongoClient()["tagRecommender"]["insgats"]
obj = {
	"tags" :  tags
}
db2.insert(obj)