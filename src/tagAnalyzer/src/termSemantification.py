from pymongo import MongoClient
import json,sys
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.Wrapper import jsonlayer
class semantification:
	def __init__(self):	

		self.config = json.load(open("./tagAnalyzer/config/config.json"))
		self.sparql = SPARQLWrapper("http://10.0.0.20:8890/sparql")
		self.termDB = MongoClient()["semantified"]["terms"]
		self.notInDbpedia = MongoClient()["nodatafount"]["terms"]
		self.termResultObject = {}
	def getTermData(self,term):
		query = self.config["query"]% (term,term)
		self.run(query)
		#query = self.config["query"]% term
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
		for each in result["results"]["bindings"]:
			uri = each["LandingURI"]["value"]
			if "disambiguation" not in uri:
				break
		uriDataObject = self.config["uriDataObject"]
		uriDataObject["uri"] = uri
		self.termResultObject["landingURI"][uri.replace(".","")] = uriDataObject
		self.termResultObject["allURI"].append(uri)

	def setDisamObject(self,result):
		uri = result["disambiguates"]["value"]
		uriDataObject = self.config["uriDataObject"]
		uriDataObject["uri"] = uri
		self.termResultObject["disamURIs"][uri.replace(".","$")] = uriDataObject
		self.termResultObject["hasDisam"] = True
		self.termResultObject["allURI"].append(uri)
	def setRedirectObject(self,result):
		self.termResultObject["hasRedirect"] = True
		uri = result["redirect"]["value"]
		uriDataObject = self.config["uriDataObject"]
		uriDataObject["uri"] = uri
		self.termResultObject["redirectPage"][uri.replace(".","$")] = uriDataObject
		self.termResultObject["allURI"].append(uri)
	def setRedirectAndDisam(self,result):
		self.termResultObject["hasDisam"] = True
		self.termResultObject["hasRedirect"] = True
		uri = result["rd"]["value"]
		uriDataObject = self.config["uriDataObject"]
		uriDataObject["uri"] = uri
		self.termResultObject["redirectPage"][uri.replace(".","$")] = uriDataObject
		uriDataObject = self.config["uriDataObject"]
		uriDataObject["uri"] = uri
		self.termResultObject["disamURIs"][uri.replace(".","$")] = uriDataObject
		self.termResultObject["allURI"].append(uri)
	def defineResultObject(self,term):
		self.termResultObject = self.config["termResultObject"]
		self.termResultObject["semantified"] = True
		self.termResultObject["term"] = term
	def processResult(self,result,term):
		if len(result["results"]["bindings"]) > 0 :
			self.defineResultObject(term)
			for eachResultFetched in result["results"]["bindings"]:
				keys = filter(lambda x : True if x != "LandingURI" and x != "term" else False , eachResultFetched.keys())
				for key in keys:
					if key == "redirect":
						self.setRedirectObject(eachResultFetched)
					elif key == "disambiguates":
						self.setDisamObject(eachResultFetched)
					else:
						self.setRedirectAndDisam(eachResultFetched)
		return self.termResultObject
	def insertFound(self,termResult) :
		self.termDB.update({"_id" : termResult["_id"]},termResult,True)
	
	def insertNotInDepdia(self,term):
		term = {"_id" : term}
		self.notInDbpedia.update({"_id" : term },term,True)

	def processTerm(self,term):
		data = self.getTermData(term.title())
		insertObj = self.processResult(data,term)
		insertObj["_id"] = insertObj["term"]
		if len(insertObj["allURI"]) > 0 :
			self.insertFound(insertObj)
		else : 
			term = insertObj["term"]
			insertObj = {}
			insertObj["_id"] = term
			self.notInDbpedia(insertObj)

	def main(self,terms):
		map(self.processTerm,terms)

if __name__ == "__main__":	
	semantify = semantification()
	semantify.main(["apples"])