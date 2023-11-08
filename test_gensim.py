from gensim.models import Word2Vec

# read corpus
corpus_file = "corpus.txt"
with open(corpus_file, "r") as file:
    corpus = file.readlines()

sentences = [sentence.strip().split() for sentence in corpus]

# train
model = Word2Vec(sentences, vector_size =100, window = 5, min_count = 1, sg = 0)

word1 = "king"
word2 = "queen"

similarity = model.wv.similarity(word1 , word2)
print(similarity)