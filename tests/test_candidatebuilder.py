import kindred

from kindred.datageneration import generateData,generateTestData
	
def test_candidatebuilder_simple():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	parser = kindred.Parser()
	parser.parse(corpus)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations = candidateBuilder.build(corpus)
	
	assert len(candidateRelations) == 4
	
	for cr in candidateRelations:
		assert len(cr.entities) == 2

	assert candidateRelations[0].entities[0].sourceEntityID == '1'
	assert candidateRelations[0].entities[1].sourceEntityID == '2'
	assert candidateRelations[1].entities[0].sourceEntityID == '2'
	assert candidateRelations[1].entities[1].sourceEntityID == '1'
	assert candidateRelations[2].entities[0].sourceEntityID == '3'
	assert candidateRelations[2].entities[1].sourceEntityID == '4'
	assert candidateRelations[3].entities[0].sourceEntityID == '4'
	assert candidateRelations[3].entities[1].sourceEntityID == '3'

	assert candidateRelations[0].relationType == None
	assert candidateRelations[1].relationType == 'treats'
	assert candidateRelations[2].relationType == None
	assert candidateRelations[3].relationType == None

	assert candidateRelations[0].argNames == None
	assert candidateRelations[1].argNames == ['obj','subj']
	assert candidateRelations[2].argNames == None
	assert candidateRelations[3].argNames == None

def test_candidatebuilder_acceptedEntityTypes():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <disease id="2">NSCLC</disease>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	parser = kindred.Parser()
	parser.parse(corpus)
	
	candidateBuilder = kindred.CandidateBuilder(acceptedEntityTypes=[('disease','drug')])
	candidateRelations = candidateBuilder.build(corpus)
	
	for cr in candidateRelations:
		assert len(cr.entities) == 2

	assert candidateRelations[0].entities[0].sourceEntityID == '2'
	assert candidateRelations[0].entities[1].sourceEntityID == '1'
	assert candidateRelations[1].entities[0].sourceEntityID == '4'
	assert candidateRelations[1].entities[1].sourceEntityID == '3'

	assert candidateRelations[0].relationType == 'treats'
	assert candidateRelations[1].relationType == None

	assert candidateRelations[0].argNames == ['obj','subj']
	assert candidateRelations[1].argNames == None

def test_candidatebuilder_triple():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer> which targets <gene id="3">EGFR</gene>. <relation type="druginfo" drug="1" disease="2" gene="3" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	parser = kindred.Parser()
	parser.parse(corpus)
	
	candidateBuilder = kindred.CandidateBuilder(entityCount=3)
	candidateRelations = candidateBuilder.build(corpus)
	
	#assert corpus.relationTypes == [('druginfo', 'disease', 'drug', 'gene')]
	for cr in candidateRelations:
		assert len(cr.entities) == 3

	assert candidateRelations[0].entities[0].sourceEntityID == '1'
	assert candidateRelations[0].entities[1].sourceEntityID == '2'
	assert candidateRelations[0].entities[2].sourceEntityID == '3'
	assert candidateRelations[1].entities[0].sourceEntityID == '1'
	assert candidateRelations[1].entities[1].sourceEntityID == '3'
	assert candidateRelations[1].entities[2].sourceEntityID == '2'
	assert candidateRelations[2].entities[0].sourceEntityID == '2'
	assert candidateRelations[2].entities[1].sourceEntityID == '1'
	assert candidateRelations[2].entities[2].sourceEntityID == '3'
	assert candidateRelations[3].entities[0].sourceEntityID == '2'
	assert candidateRelations[3].entities[1].sourceEntityID == '3'
	assert candidateRelations[3].entities[2].sourceEntityID == '1'
	assert candidateRelations[4].entities[0].sourceEntityID == '3'
	assert candidateRelations[4].entities[1].sourceEntityID == '1'
	assert candidateRelations[4].entities[2].sourceEntityID == '2'
	assert candidateRelations[5].entities[0].sourceEntityID == '3'
	assert candidateRelations[5].entities[1].sourceEntityID == '2'
	assert candidateRelations[5].entities[2].sourceEntityID == '1'

	assert candidateRelations[0].relationType == None
	assert candidateRelations[1].relationType == None
	assert candidateRelations[2].relationType == 'druginfo'
	assert candidateRelations[3].relationType == None
	assert candidateRelations[4].relationType == None
	assert candidateRelations[5].relationType == None

	assert candidateRelations[0].argNames == None
	assert candidateRelations[1].argNames == None
	assert candidateRelations[2].argNames == ['disease', 'drug', 'gene']
	assert candidateRelations[3].argNames == None
	assert candidateRelations[4].argNames == None
	assert candidateRelations[5].argNames == None

if __name__ == '__main__':
	test_candidatebuilder_acceptedEntityTypes()

