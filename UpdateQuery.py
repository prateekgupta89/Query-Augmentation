import nltk
import numpy
import math

class updateQuery():
    def __init__(self, database):
        
	self.database = database
        
	self.documents = self.tokenizeDocuments(database)
	self.wordList = self.createVocabulary()
	self.documentFrequency = self.docFrequency()

    # Tokenize the documents
    def tokenizeDocuments(self, database):
        
	documents = []
	for doc in database:
	    documents += [' '.join(word.lower() for word in nltk.word_tokenize(doc))]

	return documents

    # Vocabulary of words removing the stopwords
    def createVocabulary(self):

        stopWords = []
        words = set()
        
	stopWords = [word.rstrip('\n') for word in open('stop.txt')]

        for doc in self.documents:
	    for word in doc.split(' '):
	        if word.isalpha() and word not in stopWords:
	            words.add(word)

        return sorted(words)

    # Number of documents in the database in which a word occurs
    def docFrequency(self):
        
	wordDictionary = {}
	for doc in self.documents:
	    words = set(doc.split(' '))
	    for word in self.wordList:
	        if word in words:
	            if word in wordDictionary:
		        wordDictionary[word] += 1
	            else:
		        wordDictionary[word] = 1

	return wordDictionary

    # Function to compute Tfidf
    def computeTfidf(self, word, doc):
        # Number of times the word appers in the document
        tf = float(doc.count(word))
	# Number of documents in which the word appears
	df = float(self.documentFrequency[word])
        # Number of documents
	N = float(len(self.documents))

	if df and tf:
	    return (tf * (math.log(N/df)))
	else:
	    return 0

    # Function to get document vector
    def getDocumentVector(self):

        documentVectors = []
        for doc in self.documents:
	    docVector = []
	    for word in self.wordList:
	        tfidf = self.computeTfidf(word, doc)
		docVector.append(tfidf)
	    documentVectors.append(docVector)
	
	return documentVectors

    def getQueryVector(self, query):

        queryDoc = [' '.join(word.lower() for word in nltk.word_tokenize(query))]

        queryVector = []
	for word in self.wordList:
	    tfidf = self.computeTfidf(word, queryDoc)
            queryVector.append(tfidf)
	   
        return queryVector

    # Function to find next iteration of query 
    def getUpdatedQuery(self, relevantDocIds, query):
        
        relevantDocCount = len(relevantDocIds)
	irrelevantDocCount = len(self.database) - relevantDocCount
	vocabSize = len(self.wordList)
	ALPHA = 1.0
	BETA = 0.75
	GAMMA = 0.15

	documentVectors = self.getDocumentVector()

	queryVector = self.getQueryVector(query)

        sumRelevantDocs = [0.0] * vocabSize
	sumIrrelevantDocs = [0.0] * vocabSize

	for idx in range(0, len(self.documents)):
	    if idx in relevantDocIds:
	        sumRelevantDocs = [x + y for x, y in zip(sumRelevantDocs, documentVectors[idx])]
	    else:
	        sumIrrelevantDocs = [x + y for x, y in zip(sumIrrelevantDocs, documentVectors[idx])]

        sumRelevantDocs = numpy.asarray(sumRelevantDocs)
	sumIrrelevantDocs = numpy.asarray(sumIrrelevantDocs)
	queryVector = numpy.asarray(queryVector)

	updatedQueryVector = (ALPHA * queryVector) + ((BETA/relevantDocCount) * sumRelevantDocs) - ((GAMMA/irrelevantDocCount) * sumIrrelevantDocs)

	# Sorting the updatedQueryVector
	sortedIndices = updatedQueryVector.argsort()
	topIndices = reversed(sortedIndices[-10:])
	wordValue = [(self.wordList[idx], updatedQueryVector[idx]) for idx in topIndices]
        
          
        candidateWords = []

	for item in wordValue:
	    if item[0] not in set(query.split()):
	        candidateWords.append(item)

        augmentWordList = []
	if len(candidateWords) >= 2:
	    if candidateWords[0][1] == candidateWords[1][1]:
	        augmentWordList.append(candidateWords[0][0])
	        augmentWordList.append(candidateWords[1][0])
            else:
	        augmentWordList.append(candidateWords[0][0])
	elif len(candidateWordList) == 1:
	    augmentWordList.append(candidateWords[0][0])

        return augmentWordList
