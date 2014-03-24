import time
from pymongo import MongoClient
import json,sys
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.Wrapper import jsonlayer
class semantification:
	def __init__(self):	

		self.config = json.load(open("/Users/ankitsolanki/Desktop/tag/tagRecommender/src/tagAnalyzer/config/config.json"))
		self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		self.termDB = MongoClient()["semantified"]["terms"]
		self.notInDbpedia = MongoClient()["nodatafound"]["terms"]
		self.termResultObject = {}
	def getTermData(self,term):
		query = self.config["query"]% (term,term)
		self.run(query)
		#query = self.config["query"]% term
		return self.run(query)

	def isValidURI(self,uri):
		return "www.dbpedia.org" in uri
	def run(self,query) :
		try : 
			self.sparql.setQuery(query)
			self.sparql.setReturnFormat(JSON)
			result = self.sparql.query()
			#jsonlayer.use('cjson')
			body = result.response.read().encode('ascii','ignore')
			fixed_body = body.decode("ascii")
			result = jsonlayer.decode(fixed_body)
			return result
		except :
			print(query)
			time.sleep(60)
			self.run(query)

	def setTerm(self,result):
		self.termResultObject["term"] = result["term"]["value"]
	def setLandingObject(self,result):
		for each in result["results"]["bindings"]:
			uri = each["LandingURI"]["value"]
			if "disambiguation" not in uri:
				break
		self.termResultObject["landingURI"].append(uri)
		self.termResultObject["allURI"].append(uri)

	def setDisamObject(self,result):
		uri = result["disambiguates"]["value"]
		uriDataObject = self.config["uriDataObject"]
		uriDataObject["uri"] = uri
		self.termResultObject["disamURIs"][uri.replace(".","$")] = uriDataObject.copy()
		self.termResultObject["hasDisam"] = True
		self.termResultObject["allURI"].append(uri)
	#def setRedirectObject(self,result):
#		self.termResultObject["hasRedirect"] = True
#		uri = result["redirect"]["value"]
#		uriDataObject = self.config["uriDataObject"]
#		uriDataObject["uri"] = uri
#		self.termResultObject["redirectPage"][uri.replace(".","$")] =  uriDataObject.copy()
#		self.termResultObject["allURI"].append(uri)
#	def setRedirectAndDisam(self,result):
#		self.termResultObject["hasDisam"] = True
#		self.termResultObject["hasRedirect"] = True
#		uri = result["redirect"]["value"]
#		uriDataObject = self.config["uriDataObject"]
#		uriDataObject["uri"] = uri
#		self.termResultObject["redirectPage"][uri.replace(".","$")] =  uriDataObject.copy()
#		uriDataObject = self.config["uriDataObject"]
#		uri = result["rd"]["value"]
#		print(uriDataObject)
#		uriDataObject["uri"] = uri
#		self.termResultObject["disamURIs"][uri.replace(".","$")] =  uriDataObject.copy()
#		self.termResultObject["allURI"].append(uri)
	def defineResultObject(self,term):
		self.termResultObject = {}
		self.termResultObject = {
		"_id" : "",
		"semantified" : False,"hasRedirect" : False, "hasDisam" : False,"directDisam" : False,"reverseCheckDisam" : False,"suffixedLabelDisam" : False,
		"landingURI" : [],
		"redirect" : [],
		"allURI" : [],
		"disambiguates" : [],
		"term" : ""
		}
		self.termResultObject["semantified"] = True
		self.termResultObject["term"] = term
	def setRedirectObject(self,data) :
		if data["redirect"]["value"] not in self.termResultObject["redirect"]:
			self.termResultObject.append(data["redirect"]["value"])
	def objectUpdater(self,objkey,datakey,data):
		if datakey == "disambiguates":
			self.termResultObject["hasDisam"] = True
		elif datakey == "redirect":
			self.termResultObject["hasRedirect"] = True
		if data[datakey]["value"] not in self.termResultObject[objkey]:
			if data[datakey]["value"] not in self.termResultObject[objkey]:
				self.termResultObject[objkey].append(data[datakey]["value"])
			if data[datakey]["value"] not in self.termResultObject["allURI"]:
				self.termResultObject["allURI"].append(data[datakey]["value"])
	
	def processResult(self,result,term):
		if len(result["results"]["bindings"]) > 0 :
			self.setLandingObject(result)
			for eachResultFetched in result["results"]["bindings"]:
				keys = filter(lambda x : True if x != "LandingURI" and x != "term" else False , eachResultFetched.keys())
				for key in keys:
					if key == "redirect":
						self.objectUpdater("redirect","redirect",eachResultFetched)
					elif key == "disambiguates":
						self.objectUpdater("disambiguates","disambiguates",eachResultFetched)
					else:
						self.objectUpdater("disambiguates","rd",eachResultFetched)
						self.objectUpdater("redirect","redirect",eachResultFetched)
		return self.termResultObject
	def insertFound(self,termResult) :
		self.termDB.update({"_id" : termResult["_id"]},termResult,True)
	
	def insertNotInDepdia(self,term):
		self.notInDbpedia.update({"_id" : term["_id"] },term,True)
	def isProcessed(self,term):
		return len(list(self.termDB.find({"_id" : term})))>0 or len(list(self.notInDbpedia.find({"_id" : term}))) > 0
	def processTerm(self,term):
		term = term.replace("@@@",".")
		self.defineResultObject(term)
		if self.isProcessed(term):
			print ("term processed in previous iteration : " + term)
			return
		data = self.getTermData(term.title())

		insertObj = self.processResult(data,term)
		insertObj["_id"] = term
		if len(insertObj.keys()) > 2 :
			if len(insertObj["allURI"]) > 0 :
				self.insertFound(insertObj)
				print("Inserted term in found db : " + str(term))
			else : 
				term = insertObj["term"]
				insertObj = {}
				insertObj["_id"] = term
				self.insertNotInDepdia(insertObj)
				print("Inserted term in not found db : " + str(term))
		else :
			insertObj = {}
			insertObj["_id"] = term
			self.insertNotInDepdia(insertObj)
			print("Inserted term in not found db : " + str(term))
	def main(self,terms):
		map(self.processTerm,terms)

if __name__ == "__main__":	
	semantify = semantification()
	semantify.main(["apples","file"])