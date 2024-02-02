def clean_and_tokenize(word):
    # Remove spaces and other common symbols
    cleaned_word = ''.join(char for char in word.lower() if char.isalnum())
    return set(cleaned_word)

def jaccard_similarity(word1, word2):
    set1 = clean_and_tokenize(word1)
    set2 = clean_and_tokenize(word2)
    
    intersection_size = len(set1.intersection(set2))
    union_size = len(set1.union(set2))
    
    similarity_score = intersection_size / union_size if union_size != 0 else 0.0
    return similarity_score

word1 = "Flowrate"
word2 = "flow rate"

print(f"Jaccard sim: " + str(jaccard_similarity(word1, word2)))