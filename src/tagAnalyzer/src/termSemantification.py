from pymongo import MongoClient
import json,sys
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.Wrapper import jsonlayer
class semantification:
	def __init__(self):	

		self.config = json.load(open("../config/config.json"))
		self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		self.termDB = MongoClient()["a"]["a"]
		self.notInDbpedia = MongoClient()["b"]["b"]
		self.termResultObject = {}
	def getTermData(self,term):
		terms = [term,str(term + " (disambiguation)")]
		query = self.config["query"]% term
		return self.run(query)

	def isValidURI(self,uri):
		return "www.dbpedia.org" in uri
	def run(self,query) :
		print(query)
		self.sparql.setQuery(query)
		self.sparql.setReturnFormat(JSON)
		result = self.sparql.query()
		#jsonlayer.use('cjson')
		body = result.response.read().encode('ascii','ignore')
		fixed_body = body.decode("ascii")
		result = jsonlayer.decode(fixed_body)
		return result
	def setTerm(self,result):
		self.termResultObject["term"] = result["term"]["value"]
	def setLandingObject(self,result):
		uri = result["LandingURI"]["value"]
		
		 self.termResultObject["landingURI"][uri.replace(".","")] = {}

	def setDisamObject(self,result):

	def setRedirectObject(self,result):

	def setRedirectAndDisam(self,result):

	def processResult(self,result):
		print(result["results"]["bindings"][0].keys())
		if len(result["results"]["bindings"]) > 0 :
			self.termResultObject = self.config["termResultObject"]
			self.termResultObject["semantified"] = True
			self.termResultObject["term"] = result["results"]["bindings"][0]["term"]["value"]
			uri = uri
			self.termResultObject["LandingURI"][uri.replace(".","")] = {}
			uriDataObject = self.config["uriDataObject"]
			uriDataObject["uri"] = uri
			for eachResultFetched in result["results"]["bindings"]:
				keys = eachResultFetched.keys()

		print(termResultObject)
		return termResultObject
	def insertFound(self,termResult) :
		self.termDB.update({"_id" : termResult["_id"]},termResult,True)
	
	def insertNotInDepdia(self,term):
		term = {"_id" : term}
		self.notInDbpedia.update({"_id" : term },term,True)

	def processTerm(self,term):
		data = self.getTermData(term.title())
		self.processResult(data)

	def main(self,terms):
		map(self.processTerm,terms)

if __name__ == "__main__":	
	semantify = semantification()
	semantify.main(["india"])