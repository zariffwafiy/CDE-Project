from gensim.models import Word2Vec

# read corpus
corpus_file = "data\PETRONAS-Integrated-Report-2022.txt"
with open(corpus_file, "r", encoding="utf-8") as file:
    corpus = file.readlines()

# tokenize
sentences = [sentence.strip().split() for sentence in corpus]

# train
model = Word2Vec(sentences, vector_size =100, window = 5, min_count = 1, sg = 0)

word1 = "sustainability"
word2 = "Malaysian"

similarity = model.wv.similarity(word1.lower() , word2.lower())
print(similarity)