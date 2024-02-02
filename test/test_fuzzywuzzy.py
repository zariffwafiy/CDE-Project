from fuzzywuzzy import fuzz

word1 = "price"
word2 = "cost"

similarity_ratio = fuzz.token_sort_ratio(word1, word2)
print(f"FuzzyWuzzy ratio: {similarity_ratio}%")