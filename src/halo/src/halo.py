import json
import json,sys
import time 
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.Wrapper import jsonlayer
from pymongo import MongoClient
class halo:
	def __init__(self):
		self.config = json.load(open("../config/config.json"))
		self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		self.termDB = MongoClient()["semantified"]["terms"]
		self.halodb = MongoClient()["halo"]["halos"]
	def run(self,query):
		try:
			self.sparql.setQuery(query)
			self.sparql.setReturnFormat(JSON)
			result = self.sparql.query()
			#jsonlayer.use('cjson')
			body = result.response.read().encode('ascii','ignore')
			fixed_body = body.decode("ascii")
			result = jsonlayer.decode(fixed_body)
			return result["results"]["bindings"]
		except :
			print(query)
			time.sleep(60)
			return self.run(query)

	def makeQuery(self,uri,querykey):
		return  self.config[querykey] % (uri)
	def insert(self,obj):
		self.halodb.update({"_id":obj["_id"]},obj,True)
	def isprocessed(self,uri):
		return len(list(self.halodb.find({"_id" : uri}))) > 0
	def getHalo(self,uri):
		if not self.isprocessed(uri):
			query = self.makeQuery(uri,"queryone")
			result = self.run(query)
			query = self.makeQuery(uri,"querytwo")
			result.extend(self.run(query))
			halo = {}
			halo["_id"] = uri
			halo["uri"] = uri
			halo["halo"] = {}
			for each in result:
				halouri = each["aura"]["value"]
				halo["halo"][halouri.replace(".","$")] = {}
				obj = {}
				obj["halouri"] = halouri
				obj["count"] = each["auraCount"]["value"]
				obj["label"] = each["label"]["value"]
				halo["halo"][halouri.replace(".","$")] = obj
			self.insert(halo)
			print("processed halo for : " + uri)
		else :
			print("previously processed uri : " + uri )
	def getdatadb(self):
		return self.termDB.find(timeout=False)
	
	def processhalofromdb(self):
		data = self.getdatadb()
		for each in data :
			alluri = each["allURI"]
			map(self.getHalo,alluri)

if __name__ == "__main__":	
	h = halo()
	h.processhalofromdb()
	#h.getHalo("http://dbpedia.org/resource/Eclipse")