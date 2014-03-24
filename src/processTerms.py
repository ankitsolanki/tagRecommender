from tagAnalyzer.src.termSemantification import semantification
class processTerms:
	def __init__(self):
		self.semantifier = semantification()
	def readdata(self,path):
		terms = []
		with open(path,"r") as f:
			for term in f:
				terms.append(term.strip('\n'))
		f.close()
		return terms
	def sematify(self,terms):
		map(self.semantifier.processTerm,terms)
	def main(self,path):
		terms = self.readdata(path)
		self.sematify(terms)
		
if __name__ == "__main__":	
	process = processTerms()
	process.main("tag.csv")
