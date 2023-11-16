import pandas as pd
from collections import Counter
import math

# methodology for string comparison
# jaccard similarity
def jaccard_similarity(word1, word2):
    set1 = set(word1)
    set2 = set(word2)

    # intersection of letters
    intersection = len(set1 & set2)

    # union of letters
    union = len(set1 | set2)
    result = intersection / union
    return result 

# cosine similarity
def letter_frequency_vector(word):
    # count freq of each letter in word
    letter_counts = Counter(word)

    # create vector rep of word based on letter freq
    vector = [letter_counts.get(letter, 0) for letter in 'abcdefghijklmnopqrstuvwxyz']

    return vector

def cosine_similarity(vector1, vector2):
    dot_product = sum(x * y for x, y in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(x**2 for x in vector1))
    magnitude2 = math.sqrt(sum(y**2 for y in vector2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

def main():

    input_excel1 = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.xlsx"
    input_excel2 = "data/PETRONAS Data Standard - All -  July 2023.xlsx"

    """
    receive data document.xlsx, convert to .csv.
    choose only sheet name "DDS 3.0 Data Dictionary-Source"
    remove the first and second rows

    """ 
    # Data dictionary
    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    # Data standard
    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv" 

    data1 = pd.read_csv(data1_path)
    data2 = pd.read_csv(data2_path)

    # filter out data domain
    domains = data1["DATA DOMAIN "].iloc[0]
    data2 = data2[data2["DATA DOMAIN"].isin([domains])].reset_index(drop=True)

    # column names of data dictionary for result df
    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()

    # Prepare result_df 
    result_df = pd.DataFrame(columns=["DATA ELEMENT"])
    result_df["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # Preprocess data
    data1["FIELD NAME/DATA ATTRIBUTE(S)"] = data1["FIELD NAME/DATA ATTRIBUTE(S)"].str.lower().str.replace(r'[^a-zA-Z\s]', '', regex=True)
    data2["DATA ELEMENT"] = data2["DATA ELEMENT"].str.lower().str.replace(r'[^a-zA-Z\s]', '', regex=True)

    for word1,original_name in zip(data1["FIELD NAME/DATA ATTRIBUTE(S)"], data1_names):
        # jaccard
        # result_df[original_name] = data2["DATA ELEMENT"].apply(lambda word2: round(jaccard_similarity(word1, word2), 4))

        # cosine
        result_df[original_name] = data2["DATA ELEMENT"].apply(lambda word2: round(cosine_similarity(letter_frequency_vector(word1), letter_frequency_vector(word2)), 4))

    # transpose
    print(result_df)

    print(result_df.set_index("DATA ELEMENT").T)
    
    result_df.to_csv("result4.csv", encoding="utf-8", index=False)

if __name__ == "__main__":
    main()
