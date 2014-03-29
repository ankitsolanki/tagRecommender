import sys
import nltk
import json
from pymongo import MongoClient
import re 
from nltk import WordNetLemmatizer as wnl
class test :
	def __init__(self):	
		self.db = MongoClient()["tagRecommender"]["data_200000"]
		self.statdb = MongoClient()["tagRecommender"]["stats2"]
		self.tokenstatkeeper = MongoClient()["tokenstatkeeper"]["token"]
		self.config = json.load(open('../config/blacklist.json'))
		self.blacklisted =  list(set(self.config["blacklist"]))
		self.blacklisted =  map(lambda x : x.lower().replace("'",""),self.blacklisted)
		self.maxTermLength = self.config["maxlength"]
		self.minTermLength = self.config["minlength"]
		self.obj = {}
		self.unigramObj = {}
		self.unigramGrouper = {}
	def freqCounter (self,List):
		for each in List : 
			each = list(each)
			each[0] = re.sub(r'[^a-zA-Z0-9]', '',each[0]).lower()
			each[1] = re.sub(r'[^a-zA-Z0-9]', '',each[1]).lower()
			key = each[0]+"---tagRecomder---"+each[1]
			if each[0] == "" or each[1] == "" or each[0] == " " or each[1] == " " or each[0].isdigit() or each[1].isdigit():
				continue
			
			if key not in self.obj.keys():
				self.obj[key] = 0
			self.obj[key] = self.obj[key] + 1 
	def unigramUpdater(self,term):
		if term not in self.unigramObj.keys() :
			self.unigramObj[term] = 0
		self.unigramObj[term] = self.unigramObj[term] + 1
	def unigramUpdaterWithOtherVariable(self,tokens):
		for token in tokens:
			if token not in self.unigramGrouper.keys():
				self.unigramGrouper[token] = {}
			for t in tokens:
				if t not in self.unigramGrouper[token].keys():
					self.unigramGrouper[token][t] = 0
				self.unigramGrouper[token][t] = self.unigramGrouper[token][t] + 1 
	def tokenstatmaintainer(self,tokens):
		for token in tokens:
			tokendata = list(self.tokenstatkeeper.find({"_id" : token}))
			if len(tokendata) == 0 :
				tokendata = [{"_id" : token , "token" : token ,"stats" : {}}]
			tokendata = tokendata[0]

			for t in tokens:
				if t not in tokendata["stats"].keys():
					tokendata["stats"][t] = 0
				tokendata["stats"][t] = tokendata["stats"][t] + 1
			self.tokenstatkeeper.update({"_id" : token} , tokendata, True)
	def validTerm(self,term):
		if term is not "" and len(term) > self.minTermLength and len(term) < self.maxTermLength:
			if term not in self.blacklisted and not term.isdigit():
				return True
			else :
				return False
		return False
	def removeSpecialCharacterAndLowerTerm(self,term):
		return re.sub(r'[^a-zA-Z0-9]', '',term).lower()
	def hasNumbers(self,term):
		return any(char.isdigit() for char in term)

	# This fucntions takes in a term removes all special charaters using the regex, also replecaes the blacklisted terms.
	def validTerm(self,term):
		if term is not "" and len(term) > self.minTermLength and len(term) < self.maxTermLength:
			if term not in self.blacklisted and not term.isdigit():
				return True
			else :
				return False
		return False


	def is_ascii(self,term):
		return all(ord(letter) < 128 for letter in term)
	def bigramUpdater(self,bigram):
		print("Hellow")

		
	def cleanToken(self,term):
		term = re.sub(r'[^a-zA-Z0-9]', '',term).lower().strip()
		return term
	
	def NE_ext(self,temp):
		entity_names = []
		if hasattr(temp,'node') and temp.node:
			if temp.node == 'NE':
				entity_names.append(' '.join([child[0] for child in temp]))
			else:
				for child in temp:
					entity_names.extend(NE_ext(child))
		return entity_names
	def extractNamedEntities(self,tokens):
		tokens = nltk.pos_tag(tokens)
		entity_names = self.NE_ext(tokens)
		return entity_names

	def lemmaExtractor(self,term):
		lemma = wnl().lemmatize(term)
		if lemma == term :
			return ""
		return lemma
	def main(self):
		corpus = self.db.find({"processed" : False},timeout=False)
		processedCount = 0
		count = 0
		for each in corpus:
			each["processed"] = True
			self.db.update({"_id" : each["_id"]},each,True)
			processedCount = processedCount + 1 
			count = count + 1
			text = each["title"]
			token = nltk.word_tokenize(text)
			token = filter(self.is_ascii,token)
			token = map(self.cleanToken,token)
			token = filter(self.validTerm,token)
			bigram = nltk.bigrams(token)

			self.freqCounter(bigram)
			namedEntities = self.extractNamedEntities(token)
			
			lemmas = map(self.lemmaExtractor,token)
			lemmas = filter(lambda x: False if x == "" else True,lemmas)
			
			token.extend(lemmas)
			#map(self.unigramUpdater,token)
			#self.unigramUpdaterWithOtherVariable(token)
			self.tokenstatmaintainer(token)

			if count == 50:
				count = 0
				print("bigram key counts :" + str(len(self.obj)) + "  Unigram key count : " + str(len(self.unigramObj))+ ", processed terms : " + str(processedCount)  )
				insertObj = {
				"_id" :"intialStats-11",
				"key" : "intialStats-11",
				"statsUnigram" : self.unigramObj,
				"statsBigram" : self.obj,
				"somethg" : self.unigramGrouper
				}
				self.statdb.update({"_id" : "intialStats-11"}, insertObj, True)
			self.db.update({"_id" : each["_id"]},each,True)

if __name__ == "__main__":
	t = test()
	t.main()