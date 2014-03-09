from nltk import WordNetLemmatizer as wnl
import nltk

#Lemmatize
lemm = wnl().lemmatize('cats')
print(lemm)
#Finding Named Entity
sentence = "This is normal sentence by Neil Shah"

#Create tokens
tokens = nltk.word_tokenize(text)

#Find POS of that tokens
tokens = nltk.pos_tag(tokens)
temp = nltk.ne_chunk(tokens, binary=True)

#Function which would find NamedEntity from POS chunks
def NE_ext(temp):
    entity_names = []
    if hasattr(temp,'node') and temp.node:
        if temp.node == 'NE':
            entity_names.append(' '.join([child[0] for child in temp]))
        else:
            for child in temp:
                entity_names.extend(NE_ext(child))
    return entity_names


#Return only named entity from POS chunks
NamedEntity = NE_ext(temp)

print NamedEntity
