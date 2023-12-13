from gensim.models import Word2Vec

def train_and_compute_similarity(corpus_file, word1, word2, vector_size=100, window=5, min_count=1, sg=0):
    """
    Train a Word2Vec model on a given corpus file and compute similarity between two words.

    Parameters:
    - corpus_file (str): Path to the corpus file.
    - word1 (str): First word for similarity calculation.
    - word2 (str): Second word for similarity calculation.
    - vector_size (int): Dimensionality of the word vectors.
    - window (int): Maximum distance between the current and predicted word within a sentence.
    - min_count (int): Ignores all words with a total frequency lower than this.
    - sg (int): Training algorithm: 0 for CBOW, 1 for Skip-gram.

    Returns:
    - similarity (float): Similarity between word1 and word2.
    """
    with open(corpus_file, "r", encoding="utf-8") as file:
        corpus = file.readlines()

    # Tokenize
    sentences = [sentence.strip().split() for sentence in corpus]

    # Train Word2Vec model
    model = Word2Vec(sentences, vector_size=vector_size, window=window, min_count=min_count, sg=sg)

    # Compute similarity
    similarity = model.wv.similarity(word1.lower(), word2.lower())

    return similarity

# Example usage:
corpus_file_path = "corpus\Corpus.txt"
word1_example = "path"
word2_example = "entity"

similarity_result = train_and_compute_similarity(corpus_file_path, word1_example, word2_example)
print(similarity_result)