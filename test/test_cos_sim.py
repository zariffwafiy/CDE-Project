from collections import Counter
import math

def letter_frequency_vector(word):
    # Count the frequency of each letter in the word
    letter_counts = Counter(word)
    
    # Create a vector representation of the word based on letter frequencies
    vector = [letter_counts.get(letter, 0) for letter in 'abcdefghijklmnopqrstuvwxyz']
    
    return vector

def cosine_similarity(vector1, vector2):
    dot_product = sum(x * y for x, y in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(x**2 for x in vector1))
    magnitude2 = math.sqrt(sum(y**2 for y in vector2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0  # Handle the case where one or both vectors have zero magnitude
    
    return dot_product / (magnitude1 * magnitude2)

# Example usage
word1 = "enty"
word2 = "entity"

vector1 = letter_frequency_vector(word1)
vector2 = letter_frequency_vector(word2)

similarity = cosine_similarity(vector1, vector2)
print(f"Cosine Similarity between '{word1}' and '{word2}': {similarity}")