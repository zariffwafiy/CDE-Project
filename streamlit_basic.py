import re
import pandas as pd
import openai
import logging
import streamlit as st
import time

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI config
openai.api_type = "azure"
openai.api_base = "https://openailx.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = "3be6ba13cc1f4a16bd5293d8feba2036"

# constants
MAX_TOKENS = 100
TEMPERATURE = 0
NUM_COMPLETIONS = 1

# construct prompt
def construct_prompt(word1, word2):
    definitions = (
        "Data Attribute - It is at the lowest level of data taxonomy in a data dictionary and received from clients/businesses.\n"
        "Data Dictionary - It is a collection of data attributes.\n"
        "Data Element - It is at the lowest level of data taxonomy in a data standard and .\n"
        "Data Standard - It is a collection of data elements that is used by analyst.\n"
    )

    context = "I am comparing the semantic similarity between a data attribute in a data dictionary and a data element in a data standard."
    prompt = f"{context}\nProvide a semantic similarity score (0.xxxx) between data attribute:'{word1}' and data element:'{word2}'. Justify the score in less than 30 words based on the meaning of {word2} ."
    
    return prompt

# methodology of string comparison, openai
def openai_similarity(word1, word2):
    # openai
    try:
        # Construct a prompt for the specific input-reference pair
        prompt = construct_prompt(word1, word2)

        # Call OpenAI API for this specific input-reference pair
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

            # Extract the similarity score using a regular expression
            similarity_score_match = re.search(r'(\d+\.\d+)', result_text)
            similarity_score = round(float(similarity_score_match.group(1)), 4) if similarity_score_match else 0
        
            # Extract the justification
            # justification_match = re.search(r'\.(.+)', result_text)
            # justification = justification_match.group(1).strip() if justification_match else "No justification provided."
            
            logger.info(f"word1: {word1}")
            logger.info(f"word2: {word2}")
            logger.info(f"Similarity score: {similarity_score}")
            # logger.info(f"Justification: {justification}")

            return similarity_score

        else:
            logger.error("Error in API response.")
            return 0
        
        return similarity_score
        
    except ValueError as ve:
        logger.error(f"ValueError in comparing '{word1}' with '{word2}': {str(ve)}")

        return 0
    
    except Exception as e:
        logger.error(f"Exception in comparing '{word1}' with '{word2}': {str(e)}")

        return 0
    
def main():
    start_time = time.time()

    st.title("CDE Advisor: Semantic Similarity Comparison")
    
    # Load your data2
    data2 = pd.read_csv("data/PETRONAS Data Standard - All -  July 2023.csv")

    # Create a dropdown for the user to choose from multiple values
    filter_data2_options = data2["DATA DOMAIN"].unique().tolist()
    filter_data2 = st.selectbox("Choose Data Domain", filter_data2_options)

    # Filter data2 based on the selected value from the dropdown
    data2_filtered = data2[data2["DATA DOMAIN"] == filter_data2].reset_index(drop=True)

    field_description = st.text_area("Enter Data Attribute/Data Attribute Description:")
    
    # Assuming data2 has a column "DATA ELEMENT"
    data2_elements = data2_filtered["DATA ELEMENT"].tolist()

    if st.button("Compare"):
        # Call the OpenAI function for each data element and store the scores
        scores = [(data_element, openai_similarity(field_description, data_element)) for data_element in data2_elements]

        # Sort the scores in descending order
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # Display the top 3 highest scored comparisons and their corresponding data elements
        st.header("Top 3 Matches:")
        for i, (data_element, score) in enumerate(sorted_scores[:3]):
            st.write(f"{i+1}. {data_element}, Similarity Score: {score}")

    # Display the total running time
    total_time_seconds = time.time() - start_time
    minutes = int(total_time_seconds // 60)
    remaining_seconds = total_time_seconds % 60

    # display
    st.write(f"Running Time: {minutes} minutes and {remaining_seconds: .2f} seconds") 

if __name__ == "__main__":
    main()
