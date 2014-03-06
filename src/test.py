import sys
import nltk
from pymongo import MongoClient
import re 
class test :
	def __init__(self):	
		self.db = MongoClient()["tagRecommender"]["data"]
		self.statdb = MongoClient()["tagRecommender"]["stats"]
		self.blacklisted = ['this', 'is', 'not', 'what',  'there' , 'in' , 'my', 'when','from','to','use','how','can',"on",'the','it','that','me','often',"at",'and','which']
		self.obj = {}
		self.unigramObj = {}
	def getMegaCorpus(self):
		data = self.db.find()
		mega = ""
		for d in data:
			mega = mega + ". "+d["body"]+". " +d["title"]
		return mega
		#return reduce(lambda x,y : x["body"] + x["title"] +" " +y ,data[1:3])
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
		if self.validTerm(term):
			if term not in self.unigramObj.keys() :
				self.unigramObj[term] = 0
			self.unigramObj[term] = self.unigramObj[term] + 1

	def validTerm(self,term):
		if term is not "" or len(term) < 3:
			if term not in self.blacklisted and not term.isdigit():
				return True
			else :
				return False
		return False
	def removeSpecialCharacterAndLowerTerm(self,term):
		return re.sub(r'[^a-zA-Z0-9]', '',term).lower()
	
	# This fucntions takes in a term removes all special charaters using the regex, also replecaes the blacklisted terms.
	def cleanToken(self,term):
		term = re.sub(r'[^a-zA-Z0-9]', '',term).lower().strip()
		if term in self.blacklisted:
			return ""
		return term
	def is_ascii(self,term):
		return all(ord(letter) < 128 for letter in term)
	def bigramUpdater(self,bigram):
		print("Hellow")
	def main(self):
		corpus = self.db.find()
		processedCount = 0
		count = 0
		for each in corpus:
			
			processedCount = processedCount + 1 
			count = count + 1
			text = each["body"]+". " +each["title"]
			token = nltk.word_tokenize(text)
			token = filter (lambda x : False if x == "" or len(x) < 2 else True, map(self.cleanToken,token))
			#Discuss this Neel on this step, what you have done is removed blacklist which would mean that bigram with prop in between them would come but what about error?? Precision vs Recall debate!
			map(self.unigramUpdater,token)
			
			bigram = nltk.bigrams(token)
			self.freqCounter(bigram)
			if count == 50 :
				count = 0
				print("bigram key counts :" + str(len(self.obj)) + "  Unigram key count : " + str(len(self.unigramObj))+ ", processed terms : " + str(processedCount)  )
				insertObj = {
				"_id" :"intialStats-5",
				"key" : "intialStats-5",
				"statsBigram" : self.obj,
				"statsUnigram" : self.unigramObj
				}
				self.statdb.update({"_id" : "intialStats-5"}, insertObj, True)
if __name__ == "__main__":
	t = test()
	t.main()