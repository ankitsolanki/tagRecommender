
import sys
import nltk
import json
from pymongo import MongoClient
import re 
from nltk import WordNetLemmatizer as wnl
class test :
	def __init__(self):	
		self.db = MongoClient()["tagRecommender"]["data_200000"]
		self.statdb = MongoClient()["tagRecommender"]["stats"]
		self.config = json.load(open('../config/blacklist.json'))
		self.blacklisted =  list(set(self.config["blacklist"]))
		self.blacklisted =  map(lambda x : x.lower().replace("'",""),self.blacklisted)
		self.maxTermLength = self.config["maxlength"]
		self.minTermLength = self.config["minlength"]
		self.obj = {}
		self.unigramObj = {}
#	def getMegaCorpus(self):
#		data = self.db.find()
#		mega = ""
#		for d in data:
#			mega = mega + ". "+d["body"]+". " +d["title"]
#		return mega
#		#return reduce(lambda x,y : x["body"] + x["title"] +" " +y ,data[1:3])
	def freqCounter (self,List):
		for each in List : 
			#Temporary Fix... for mongo as mongo doesnt accept . in keys ! 
			# Rewrite using regular expression later....
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
		if term in self.blacklisted or term.isdigit():
			return ""
		elif len(term) < self.minTermLength or len(term) > self.maxTermLength:
			return ""
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
		print(term)
		lemma = wnl().lemmatize(term)
		if lemma == term :
			return ""
		return lemma
	def main(self):
	#	try : 
		if True:
			corpus = self.db.find(timeout=False)
			processedCount = 0
			count = 0
			for each in corpus[5:7]:
				processedCount = processedCount + 1 
				count = count + 1
				text = each["body"]+". " +each["title"]
				token = nltk.word_tokenize(text)
				token = filter(self.is_ascii,token)
				token = filter(self.validTerm,token)
				
				namedEntities = self.extractNamedEntities(token)
				lemmas = map(self.lemmaExtractor,token)
				token.extend(lemmas)
				#token = filter (lambda x : False if x == "" or len(x) < 3 or self.hasNumbers(x) or not self.validTerm(x) else True, map(self.cleanToken,token))
				#Discuss this Neel on this step, what you have done is removed blacklist which would mean that bigram with prop in between them would come but what about error?? Precision vs Recall debate!
				map(self.unigramUpdater,token)
				
				#bigram = nltk.bigrams(token)
			#	self.freqCounter(bigram)
				if count == 50 :
					count = 0
					print("bigram key counts :" + str(len(self.obj)) + "  Unigram key count : " + str(len(self.unigramObj))+ ", processed terms : " + str(processedCount)  )
					insertObj = {
					"_id" :"intialStats-9",
					"key" : "intialStats-9",
					"statsUnigram" : self.unigramObj
					}
					self.statdb.update({"_id" : "intialStats-9"}, insertObj, True)
	#	except :
	#		for eachUnigram in self.unigramObj.keys():
	#			print(eachUnigram + "," + str(self.unigramObj[eachUnigram] ))




if __name__ == "__main__":
	t = test()
	t.main()