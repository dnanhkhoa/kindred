
import json

from pycorenlp import StanfordCoreNLP

import kindred
from intervaltree import Interval, IntervalTree
from collections import defaultdict

def shortenDepName(depName):
	acceptedSubNames = set(['acl:relcl','cc:preconj','compound:prt','det:predet','nmod:npmod','nmod:poss','nmod:tmod'])
	if depName in acceptedSubNames:
		return depName
	else:
	 	return depName.split(":")[0]

class Parser:
	def __init__(self):
		pass

	nlp = None

	def parse(self,data):
		assert isinstance(data,list)
		for d in data:
			assert isinstance(d,kindred.RelationData) or isinstance(d,kindred.TextAndEntityData)

		if Parser.nlp is None:
			Parser.nlp = StanfordCoreNLP('http://localhost:9000')

		allSentenceData = []
		for d in data:
			entityIDsToSourceEntityIDs = d.getEntityIDsToSourceEntityIDs()
		
			denotationTree = IntervalTree()
			entityTypeLookup = {}
			for e in d.getEntities():
				entityTypeLookup[e.entityID] = e.entityType
			
				for a,b in e.pos:
					denotationTree[a:b] = e.entityID
					
			parsed = Parser.nlp.annotate(d.getText(), properties={'annotators': 'tokenize,ssplit,lemma,pos,depparse,parse','outputFormat': 'json'})
	
			#print type(parsed)
			

			for sentence in parsed["sentences"]:
				#print sentence.keys()
				#assert False
				tokens = []
				for t in sentence["tokens"]:
					#kindred.Token(token,pos,lemma,start,end)
					token = kindred.Token(t["word"],t["pos"],t["lemma"],t["characterOffsetBegin"],t["characterOffsetEnd"])
					tokens.append(token)

				dependencies = []
				#for de in sentence["enhancedPlusPlusDependencies"]:
				for de in sentence["collapsed-ccprocessed-dependencies"]:
					#depName = de["dep"].split(":")[0]
					depName = shortenDepName(de["dep"])
					#if depName == 'nmod:in_addition_to':
						#print de
					#	print json.dumps(sentence,indent=2,sort_keys=True)
					#	print d.getText()
					#	assert False
					#print "DEPNAME", depName
					dep = (de["governor"]-1,de["dependent"]-1,depName)
					dependencies.append(dep)
				# TODO: Should I filter this more or just leave it for simplicity
					
				entityIDsToTokenLocs = defaultdict(list)
				for i,t in enumerate(tokens):
					entitiesOverlappingWithToken = denotationTree[t.startPos:t.endPos]
					for interval in entitiesOverlappingWithToken:
						entityID = interval.data
						entityIDsToTokenLocs[entityID].append(i)

				# Let's gather up the information about the "known" entities in the sentence
				#entityLocs, entityTypes = {},{}
				processedEntities = []
				for entityID,entityLocs in sorted(entityIDsToTokenLocs.items()):
					entityType = entityTypeLookup[entityID]
					sourceEntityID = entityIDsToSourceEntityIDs[entityID]
					processedEntity = kindred.ProcessedEntity(entityType,entityLocs,entityID,sourceEntityID)
					#entityLocs[entityID] = locs
					#entityTypes[entityID] = entityType
					processedEntities.append(processedEntity)
					
				relations = []
				# Let's also put in the relation information if we can get it
				if isinstance(d,kindred.RelationData):
					tmpRelations = d.getRelations()
					entitiesInSentence = entityIDsToTokenLocs.keys()
					for tmpRelation in tmpRelations:
						matched = [ (relationEntityID in entitiesInSentence) for relationEntityID in tmpRelation.entityIDs ]
						if all(matched):
							relations.append(tmpRelation)
					
				sentenceData = kindred.ProcessedSentence(tokens, dependencies, processedEntities, relations, d.getSourceFilename())
				allSentenceData.append(sentenceData)
		return allSentenceData
	
	#return allSentenceData
