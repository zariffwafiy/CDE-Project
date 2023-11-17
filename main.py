import pandas as pd
from collections import Counter
import math
import pickle
from models import LanguageNgramModel, MissingLetterModel
from abbreviation_spellchecker import noisy_channel
from gensim.models import Word2Vec
import spacy

# methodology for string comparison
# spaCy model
# nlp = spacy.load("en_core_web_lg")
nlp = "" # dummy

def semantic_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)

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

def load_and_apply_models(input_string, model_path):
    with open(model_path, 'rb') as model_file:
        big_lang_model, big_missing_model, _ = pickle.load(model_file)

    result = noisy_channel(input_string, big_lang_model, big_missing_model, max_attempts=1000, optimism=0.9, freedom=3.0, verbose=False)
    return result, big_lang_model, big_missing_model

def main():

    """
    receive data document.xlsx, convert to .csv.
    choose only sheet name "DDS 3.0 Data Dictionary-Source"
    remove the first and second rows

    """ 
    # Data Dictionary
    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    data1 = pd.read_csv(data1_path).head(5)
    # Data Standard
    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv" 
    data2 = pd.read_csv(data2_path)

    # filter out data domain
    # domains = data1["DATA DOMAIN "].iloc[0]
    # data2 = data2[data2["DATA DOMAIN"].isin([domains])].reset_index(drop=True)

    # column names of data dictionary for result df
    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()

    # Prepare result_df 
    result_df = pd.DataFrame(columns=["DATA ELEMENT"])
    result_df["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # Preprocess data with regex
    data1["FIELD NAME/DATA ATTRIBUTE(S)"] = data1["FIELD NAME/DATA ATTRIBUTE(S)"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    # Remove "System generated field:" from "FIELD DESCRIPTION"
    data1["FIELD DESCRIPTION"] = data1["FIELD DESCRIPTION"].str.replace(r'System generated field:', '', case=False, regex=True)
    data1["FIELD DESCRIPTION"] = data1["FIELD DESCRIPTION"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True) # "System generated field:" is present in all rows, should remove
    data1["TABLE NAME"] = data1["TABLE NAME"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data1["TABLE DESCRIPTION/SUB FOLDER NAME "] = data1["TABLE DESCRIPTION/SUB FOLDER NAME "].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data2["DATA ELEMENT"] = data2["DATA ELEMENT"].str.lower().str.replace(r'[^a-zA-Z\s]', '', regex=True)

    # load and apply abbreviation spellchecker to all data dictionary data attributes
    """
    for i, data1_name in enumerate(data1_names):
        # choose each value from data
        word1 = data1["FIELD NAME/DATA ATTRIBUTE(S)"].iloc[i]

        # load and apply models to each value
        result, _, _ = load_and_apply_models(word1.lower(), model_path="abbreviation_spellchecker.pkl")

        # replace original value with result
        data1.at[i, "FIELD NAME/DATA ATTRIBUTE(S)"] = result

    """

    corpus_file = "corpus\Corpus.txt"

    # iterate to apply cosine similarity model
    for field_name, field_description, table_name, table_description, original_name in zip(
            data1["FIELD NAME/DATA ATTRIBUTE(S)"], data1["FIELD DESCRIPTION"], data1["TABLE NAME"], data1["TABLE DESCRIPTION/SUB FOLDER NAME "], data1_names
        ):
        """
        # Calculate cosine similarity scores for each combination
        score1 = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                cosine_similarity(
                    letter_frequency_vector(str(table_name)),
                    letter_frequency_vector(str(data_element))
                ),
                4,
            )
        )
        score2 = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                cosine_similarity(
                    letter_frequency_vector(str(table_description)),
                    letter_frequency_vector(str(data_element))
                ),
                4,
            )
        )
        score3 = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                cosine_similarity(
                    letter_frequency_vector(str(field_name)),
                    letter_frequency_vector(str(data_element))
                ),
                4,
            )
        )
        score4 = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                cosine_similarity(
                    letter_frequency_vector(str(field_description)),
                    letter_frequency_vector(str(data_element))
                ),
                4,
            )
        )
        score5 = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                cosine_similarity(
                    letter_frequency_vector(str(table_name) + str(table_description)),
                    letter_frequency_vector(str(data_element))
                ),
                4,
            )
        )
        # Calculate the average score for each combination
        result_df[original_name] = (score1 + score2 + score3 + score4 + score5) / 5
        """
        # spacy
        """
        result_df[original_name] = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                semantic_similarity(
                    field_description, 
                    data_element
                ), 
                4
            )
        )
        """

        # jaccard sim
        """
        result_df[original_name] = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                jaccard_similarity(
                    field_description, 
                    data_element
                ), 
                4
            )
        )
        """

        # syntax cosine sim
        result_df[original_name] = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                cosine_similarity(
                    letter_frequency_vector(field_description), 
                    letter_frequency_vector(data_element)
                ), 
                4,
            )
        )

        """
        # semantic cosine sim
        result_df[original_name] = data2["DATA ELEMENT"].apply(
            lambda data_element: round(
                train_and_compute_similarity(
                    corpus_file, 
                    field_description, 
                    data_element
                ), 
                4
            )
        )
        """

    # transpose if needed
    # result_df = result_df.set_index("DATA ELEMENT").T

    output_path = "results/result_cossim.csv"
    result_df.to_csv(output_path, encoding="utf-8", index=False)

if __name__ == "__main__":
    main()
