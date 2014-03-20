import json
import json,sys
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.Wrapper import jsonlayer
class halo:
	def __init__(self):
		self.config = json.load(open("../config/config.json"))
		self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	def run(self,query):
		print(query)
		self.sparql.setQuery(query)
		self.sparql.setReturnFormat(JSON)
		result = self.sparql.query()
		#jsonlayer.use('cjson')
		body = result.response.read().encode('ascii','ignore')
		fixed_body = body.decode("ascii")
		result = jsonlayer.decode(fixed_body)
		return result["results"]["bindings"]

	def makeQuery(self,uri,querykey):
		return  self.config[querykey] % (uri)

	def getHalo(self,uri):
		query = self.makeQuery(uri,"queryone")
		result = self.run(query)
		query = self.makeQuery(uri,"querytwo")
		result.extend(self.run(query))
		print(len(result))
if __name__ == "__main__":	
	h = halo()
	h.getHalo("http://dbpedia.org/resource/Eclipse")