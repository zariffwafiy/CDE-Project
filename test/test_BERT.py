from sentence_transformers import SentenceTransformer, util
import torch

class SemanticSimilarityMatcher:
    def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def encode_text(self, text):
        return self.model.encode(text, convert_to_tensor=True)

    def calculate_similarity(self, text1, text2):
        # Encode the texts
        embeddings1 = self.encode_text(text1)
        embeddings2 = self.encode_text(text2)

        # Calculate cosine similarity
        similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2)[0][0].item()
        return similarity_score

if __name__ == "__main__":
    matcher = SemanticSimilarityMatcher()

    # Example usage
    text1 = "Natural language processing is a subfield of artificial intelligence."
    text2 = "NLP is a branch of AI."

    similarity_score = matcher.calculate_similarity(text1, text2)
    print(f"Semantic Similarity Score: {similarity_score}")
