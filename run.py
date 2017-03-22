import sys
import base64
import urllib2,json
from UpdateQuery import updateQuery

class Bing:
    def __init__(self, query, precision, key):
        self.query = query
	self.precision = precision
	self.accountKey = key
	self.relevantResults = []
	self.data = None
	self.key = base64.b64encode(self.accountKey + ':' + self.accountKey)

    def fetchQueryResult(self):
        queryWords = self.query.split(' ')
        if len(queryWords) > 1:
	    searchQuery = '%20'.join(word for word in queryWords)
	else:
	    searchQuery = self.query
	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'+searchQuery+'%27&$top=10&$format=json'
        headers = {'Authorization': 'Basic ' + self.key}

        print 'Parameters:'
	print 'Client key = %s' % self.accountKey
	print 'Query = %s' % self.query
	print 'Precision = %f' % self.precision
	print 'URL: %s' % bingUrl

	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
        content = response.read()
	data = json.loads(content)
	self.data = data

    def printQueryResult(self):
        result = self.data.get('d').get('results')
	user_input = ['y', 'n', 'Y', 'N']

        print 'Total no of results : %d' % len(result)
	print 'Bing Search Results:'
	print '======================'
	for i in range(len(result)):
	    value = result[i] 
	    print 'Result %d' %(i+1)
	    print '['
	    print 'URL: %s' % value['Url']
	    print 'Title: %s' % value['Title']
	    print 'Summary: %s' % value['Description']
	    print ']'
            
	    isRelevant = raw_input("Relevant (Y/N)?").strip()
	    while isRelevant not in user_input:
	        print 'Please enter Y or y(for Yes) and N or n(for No)'
		isRelevant = raw_input("Relevant (Y/N)?")
            
            if isRelevant == 'y' or isRelevant == 'Y':
	        self.relevantResults += [i]

    def evaluateResult(self):
        achieved_precision = len(self.relevantResults)/10.0
	print '======================'
	print 'FEEDBACK SUMMARY'
	print 'Query %s' %self.query
	print 'Precision %f' % achieved_precision

	if achieved_precision >= self.precision:
	    print 'Desired precision reached, done'
	    sys.exit()
	    
        elif achieved_precision < self.precision:
	    print 'Still below the desired precision of %f' %self.precision
	    print 'Indexing results ....'
	    print 'Indexing results ....'
	    if achieved_precision == 0.0:
	        print 'Augmenting by'
	        print 'Below desired precision, but can no longer augment the query'
	    else:
	        self.updateSearchQuery()

    def updateSearchQuery(self):
        result = self.data.get('d').get('results')
	database=[]
	for item in result:
            database += [item["Description"].encode('ascii', 'ignore') + item['Title'].encode('ascii', 'ignore')]
	
	db = updateQuery(database)

        augmentWordList = db.getUpdatedQuery(self.relevantResults, self.query)

        for word in augmentWordList:
	    self.query += ' ' + word

	self.query.rstrip()
	self.relevantResults = []
        self.fetchQueryResult()
        self.printQueryResult()
        self.evaluateResult() 

        return

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print 'Missing arguments. Please enter in the following format:'
        print 'python run.sh <bing account key> <precision> <query>' 
        sys.exit()

    accountKey = sys.argv[1]
    query = ''
    for i in range(3, len(sys.argv)):
        query += sys.argv[i] + ' '
    query = query.rstrip()
    precision = float(sys.argv[2])
    while (precision > 1) or (precision < 0):
       print 'Precision must be between 0 and 1. Please enter a valid value.'
       precision = float(raw_input("Enter target precision:"))
    
    bingSearch = Bing(query=query, precision=precision, key = accountKey)
    bingSearch.fetchQueryResult()
    bingSearch.printQueryResult()
    bingSearch.evaluateResult() 
