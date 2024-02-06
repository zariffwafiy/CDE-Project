import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

# Download the NLTK resources if not already downloaded
import nltk
nltk.download('stopwords')

# Function to preprocess and calculate Jaccard similarity
def jaccard_similarity(str1, str2):
    # Remove punctuations, symbols, and convert to lowercase
    str1 = re.sub(r'[^\w\s]', '', str1).lower()
    str2 = re.sub(r'[^\w\s]', '', str2).lower()

    # Create sets of individual letters
    set1 = set(''.join(str1.split()))
    set2 = set(''.join(str2.split()))

    # Calculate Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity = intersection / union if union > 0 else 0
    return similarity

# Input strings
word1 = "sensor tagging"
word2 = "Real-Time thickness Sensor Tagging"

# Calculate Jaccard similarity
similarity_score = jaccard_similarity(word1, word2)

# Print the result
print(f"Jaccard Similarity between '{word1}' and '{word2}': {similarity_score}")
