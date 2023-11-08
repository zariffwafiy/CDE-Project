import spacy

# load the spaCy model
nlp = spacy.load("en_core_web_lg")

def semantic_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)

text1 = "irritation"
text2 = "irritating"
similarity = semantic_similarity(text1, text2)
print(similarity)

