import re
import pandas as pd
import openai
import logging
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import time
from functools import partial

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_TOKENS = 15
TEMPERATURE = 0
NUM_COMPLETIONS = 1

def configure_openai():
    openai.api_type = "azure"
    openai.api_base = "https://openailx.openai.azure.com/"
    openai.api_version = "2022-12-01"
    openai.api_key = "3be6ba13cc1f4a16bd5293d8feba2036"

def construct_prompt(word1, word2, word3):
    definitions = (
        "Data Attribute - It is at the lowest level of data taxonomy in a data dictionary and received from clients/businesses.\n"
        "Data Dictionary - It is a collection of data attributes.\n"
        "Data Element - It is at the lowest level of data taxonomy in a data standard and .\n"
        "Data Standard - It is a collection of data elements that is used by analyst.\n"
    )

    context = "I am comparing the semantic similarity between a data attribute in a data dictionary and a data element in a data standard."
    
    prompt = (
        f"{definitions}\n{context}\n"
        f"Provide a precise semantic similarity score (0.xxxx) between data attribute: '{word1}' "
        f"and data element: '{word2}'. '{word2}' is defined as: '{word3}'. Justify the score in less than 10 words."
    )

    return prompt

def openai_similarity(word1, word2, word3):
    try:
        prompt = construct_prompt(word1, word2, word3)

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            n=NUM_COMPLETIONS,
            stop=None,
            logprobs=0
        )

        if response and response.choices:
            result_text = response.choices[0].text

            similarity_score_match = re.search(r'(\d+\.\d+)', result_text)
            similarity_score = round(float(similarity_score_match.group(1)), 4) if similarity_score_match else 0

            justification_match = re.search(r'\.(.+)\.', result_text)
            justification = justification_match.group(1).strip() if justification_match else "No justification provided."

            logger.info(f"word1: {word1}")
            logger.info(f"word2: {word2}")
            logger.info(f"Similarity score: {similarity_score}")
            logger.info(f"Justification: {justification}")

            return word1, word2, similarity_score, word3

        else:
            return word1, word2, 0, "Error in API response"

    except ValueError as ve:
        return word1, word2, 0, str(ve)

    except Exception as e:
        return word1, word2, 0, str(e)

def main():
    st.title("CDE Advisor: Semantic Similarity Comparison")

    # Load your standard
    standard = pd.read_csv("data/PETRONAS Data Standard - All -  July 2023.csv")

    # Create a dropdown for the user to choose from multiple values
    filter_standard_options = standard["DATA DOMAIN"].str.strip().unique().tolist()
    filter_standard = st.selectbox("Choose Data Domain", filter_standard_options)

    # Filter standard based on the selected value from the dropdown
    standard_filtered = standard[standard["DATA DOMAIN"] == filter_standard].reset_index(drop=True)

    field_description = st.text_area("Enter Field Description/Field Attribute:")

    # data standard column "DATA ELEMENT"
    standard_elements = standard_filtered["DATA ELEMENT"].tolist()
 
    # data standard columns "BUSINESS DEFINITION/ GLOSSARY"
    standard_glossary = standard_filtered["BUSINESS DEFINITION/ GLOSSARY"].tolist()

    # data standard column "DATA GROUP"
    standard_group = standard_filtered["DATA GROUP"].tolist()

    # data standard column "DATA ENTITY"
    standard_entity = standard_filtered["DATA ENTITY"].tolist()

    # element glossary pairs
    element_glossary_pairs = zip(standard_elements, standard_glossary)

    if st.button("Compare"):
        start_time = time.time()

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers = 3) as executor:
            # Use the executor to process each data element concurrently
            scores = list(executor.map(lambda x: openai_similarity(field_description, x[0], x[1]), element_glossary_pairs))

        # Sort the scores in descending order based on the inner tuple's second element
        sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)

        # Display the top 3 highest scored comparisons and their corresponding data elements
        st.header("Top 3 Matches:")
        for i, (word1, word2, score, word3) in enumerate(sorted_scores[:3]):
            st.text(f"{i+1}. Data Element: {word2}\n Similarity Score: {score}\n Glossary: {word3}. \n" + " Data Group: " + standard_group[i+1] + "\n" + " Data Entity: " + standard_entity[i+1] + "\n")

        # Display the total running time in minutes and seconds
        total_time_seconds = time.time() - start_time
        minutes = int(total_time_seconds // 60)
        remaining_seconds = total_time_seconds % 60
        st.write(f"Running Time: {minutes} minutes and {remaining_seconds: .2f} seconds") 

if __name__ == "__main__":
    configure_openai()
    main()
