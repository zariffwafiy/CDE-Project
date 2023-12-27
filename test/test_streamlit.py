import streamlit as st
import pandas as pd
import time
import logging
import openai
import re
from concurrent.futures import ThreadPoolExecutor

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# constants
MAX_TOKENS = 50
TEMPERATURE = 0
NUM_COMPLETIONS = 1

def configure_openai():
    """
    Configures the OpenAI API by setting the API type, base URL, version, and key.

    This function sets the `api_type` property of the `openai` module to "azure",
    indicating that the Azure variant of the OpenAI API should be used. It also
    sets the `api_base` property to "https://openailx.openai.azure.com/" to specify
    the base URL for API requests, and the `api_version` property to "2022-12-01" to
    indicate the version of the API to use. Finally, it sets the `api_key` property
    to "3be6ba13cc1f4a16bd5293d8feba2036" to provide the authentication key for API
    requests.

    This function does not take any parameters and does not return any values.
    """
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
        f"and data element: '{word2}'. '{word2}' is defined as: '{word3}'."
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

            # justification_match = re.search(r'\.(.+)\.', result_text)
            # justification = justification_match.group(1).strip() if justification_match else "No justification provided."

            logger.info(f"word1: {word1}")
            logger.info(f"word2: {word2}")
            logger.info(f"Similarity score: {similarity_score}")

            return word1, word2, similarity_score

        else:
            return word1, word2, 0, "Error in API response"

    except ValueError as ve:
        return word1, word2, 0, str(ve)

    except Exception as e:
        return word1, word2, 0, str(e)

def process_data_element():
    pass

def main():
    configure_openai()

    start_time = time.time()

    st.title("Semantic Similarity Comparison")
    
    # Load your data2
    data2 = pd.read_csv("data/PETRONAS Data Standard - All -  July 2023.csv")

    # Create a dropdown for the user to choose from multiple values
    filter_data2_options = data2["DATA DOMAIN"].unique().tolist()
    filter_data2 = st.selectbox("Choose Data Domain", filter_data2_options)

    # Filter data2 based on the selected value from the dropdown
    data2_filtered = data2[data2["DATA DOMAIN"] == filter_data2].reset_index(drop=True).head(5)

    field_description = st.text_area("Enter Field Description:")
    
    # Assuming data2 has a column "DATA ELEMENT"
    data2_elements = data2_filtered["DATA ELEMENT"].tolist()

    if st.button("Compare"):
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            # Use the executor to process each data element concurrently
            scores = list(executor.map(lambda elem: process_data_element(elem, field_description), data2_elements))

        # Print the structure of a single element in scores for debugging
        print("Example scores element:", scores[0])

        # Sort the scores in descending order based on the inner tuple's second element
        sorted_scores = sorted(scores, key=lambda x: x[1][1] if isinstance(x[1], tuple) else x[1], reverse=True)

        # Display the top 3 highest scored comparisons and their corresponding data elements
        st.header("Top 3 Matches:")
        for i, (field_element, score_info) in enumerate(sorted_scores[:3]):
            if isinstance(score_info, tuple):
                data_element, score = score_info
                st.write(f"{i+1}. Field Element: {field_element}, Data Element: {data_element}, Similarity Score: {score}")
            else:
                st.write(f"{i+1}. Field Element: {field_element}, Similarity Score: {score_info}")

        # Display the total running time
        total_time = time.time() - start_time
        st.write(f"Total Running Time: {total_time:.2f} seconds")


if __name__ == "__main__":
    main()
