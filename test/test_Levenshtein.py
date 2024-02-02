import Levenshtein

word1 = "price"
word2 = "cumulunimbus"

levenshtein_distance = Levenshtein.distance(word1, word2)
levenshtein_score = 1 / (1 + levenshtein_distance)
print(f"Levenshtein Distance: {levenshtein_distance}")