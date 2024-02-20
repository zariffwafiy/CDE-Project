import re
import time
import logging
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import streamlit as st
import openai
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

nltk.download('stopwords')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_TOKENS = 50
TEMPERATURE = 0.2
NUM_COMPLETIONS = 1
ENGINE = "CDE-Advisor"
LOG_PROBS = 0

# Custom Exception for Rate Limit Exceeded
class RateLimitExceededException(Exception):
    pass

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

def configure_openai():
    openai.api_type = "azure"
    openai.api_base = "https://ptsg5edhopenai01.openai.azure.com/"
    openai.api_version = "2023-09-15-preview"
    openai.api_key = "d929ffb032eb4ef186804b69cbb95531"
    
def construct_prompt(word1, word2, word3):
    definitions = (
        "Data Attribute - It is at the lowest level of data taxonomy in a data dictionary and received from businesses.\n"
        "Data Dictionary - It is a collection of data attributes.\n"
        "Data Element - It is at the lowest level of data taxonomy in a data standard and .\n"
        "Data Standard - It is a collection of data elements that is used by analyst.\n"
    )

    context = "I am comparing the semantic similarity between a data attribute in a data dictionary and a data element in a data standard."
    
    prompt = (
        f"{definitions}\n{context}\n"
        f"Provide a precise semantic similarity score in four decimal places(0.xxxx) between data attribute: '{word1}' "
        f"and data element: '{word2}'. '{word2}' is defined as: '{word3}'. Justify the score in less than 10 words."
    )

    return prompt

def openai_similarity(word1, word2, word3, group, entity):
    try:
        prompt = construct_prompt(word1, word2, word3)

        response = openai.Completion.create(
            engine=ENGINE,
            prompt=prompt,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            n=NUM_COMPLETIONS,
            stop=None,
            logprobs=LOG_PROBS
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

            return word1, word2, similarity_score, word3, group, entity

        else:
            return word1, word2, 0, "Error in API response"

    except ValueError as ve:
        return word1, word2, 0, str(ve)

    except Exception as e:
        error_message = str(e)

        if "rate limit" in error_message.lower():
            st.error("**OpenAI rate limit exceeded. Someone else is using the tool .please try again later.**")
            raise RateLimitExceededException("OpenAI rate limit exceeded. Someone else is using the tool. Please try again later.")
        else: return word1, word2, 0, error_message

def main():
    try:
        # set page configuration 
        st.set_page_config(
            page_title="CDE Advisor: Semantic Similarity Comparison",
            page_icon=":oil_drum:",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # HTML and CSS for setting background image and additional styles
        background_html = """
        <style>
            h1 {
                text-align: center; /* Center-align header text */
            }

            .stDeployButton {
                visibility: hidden;
            }
        </style>
        """ 
        raise RateLimitExceededException("The program is unusable for awhile. Please contact the author or try again after 2 days.")
 
        # Display the HTML with the background image
        st.markdown(background_html, unsafe_allow_html=True)

        logo_image = "assets/petronas.png"

        # Add sidebar for documentation  
        st.sidebar.image(logo_image, width = 200)
        st.sidebar.header("About")
        st.sidebar.markdown("This is a simple prototype to compare the semantic similarity between a data attribute in a data dictionary and a data element in a data standard.")
        st.sidebar.header("How to Use")
        st.sidebar.markdown("Please filter out the domain of the data dictionary and enter the data attribute/ data attribute description in the text area below. Choose the number of matches to be displayed using the slider.")
        st.sidebar.markdown("The semantic similarity score and glossary will be displayed on for each of the corresponding data element.")
        st.sidebar.divider()
        st.sidebar.info("**Data Scientist: [@zariffwafiy](https://github.com/zariffwafiy)**", icon="🧠")
        
        st.title("📖CDE Advisor: Semantic Similarity Comparison")
        st.write("")
        st.write("")

        uploaded_file = st.file_uploader("**Please upload the latest PETRONAS Data Standard**", type = ["xlsx"])

        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            st.write("")

            # read excel file
            standard = pd.read_excel(uploaded_file)

            # Create a dropdown for the user to choose from multiple values
            filter_standard_options = standard["DATA DOMAIN"].unique().tolist()
            filter_standard_options = ["All"] + filter_standard_options

            # Create a dropdown for the user to choose from multiple values
            filter_standard = st.selectbox("**Choose Data Domain**", filter_standard_options, index = 0)
            st.write("")

            # Apply the condition
            if "All" in filter_standard:
                standard_filtered = standard

            else:
                # Get the first part before "("
                selected_category = filter_standard

                # Filter the dataframe based on the selected category
                standard_filtered = standard[standard["DATA DOMAIN"].str.strip() == selected_category].reset_index(drop=True)

            data_input = st.text_area("**Enter Data Attribute/ Data Attribute Description:**")

            num_matches_slider = st.slider("**Select the number of top matches to display (between 1 and 10)**", min_value=1, max_value=10, value=3)

            # Calculate Jaccard similarity scores for each data element in 'standard_filtered'
            jaccard_scores = standard_filtered['DATA ELEMENT'].apply(lambda elem: jaccard_similarity(data_input, elem))
            
            # Add the Jaccard similarity scores as a new column to 'standard_filtered'
            standard_filtered['JACCARD_SCORE'] = jaccard_scores

            # Sort 'standard_filtered' based on Jaccard similarity scores in descending order
            sorted_standard_filtered = standard_filtered.sort_values(by='JACCARD_SCORE', ascending=False).reset_index().head(150)

            # data standard column "DATA ELEMENT"
            standard_elements = sorted_standard_filtered["DATA ELEMENT"].tolist()
        
            # data standard columns "BUSINESS DEFINITION/ GLOSSARY"
            standard_glossary = sorted_standard_filtered["BUSINESS DEFINITION/ GLOSSARY"].tolist()

            # data group columns "DATA GROUP"
            standard_group = sorted_standard_filtered["DATA GROUP"].tolist()

            # data entity columns "DATA ENTITY"
            standard_entity = sorted_standard_filtered["DATA ENTITY"].tolist()

            # element glossary pairs
            standard_info = zip(standard_elements, standard_glossary, standard_group, standard_entity)

            if st.button("Compare"):
                st.header("Top Matches:")

                start_time = time.time()

                # Use ThreadPoolExecutor for parallel processing
                with ThreadPoolExecutor(max_workers = 2) as executor:
                    # Use the executor to process each data element concurrently, semantic similarity matching
                    scores = list(executor.map(lambda x: openai_similarity(data_input, x[0], x[1], x[2], x[3]), standard_info))

                # Sort the scores in descending order based on the inner tuple's second element
                sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)

                # Display the top 3 highest scored comparisons and their corresponding data elements
                for i, (word1, word2, score, word3, group, entity) in enumerate(sorted_scores[:num_matches_slider]):
                    st.text(f"{i+1}. Data Element: {word2}\n Similarity Score: {score}\n Glossary: {word3}. \n Data Group: {group}\n Data Entity: {entity}\n")

                # Display the total running time in minutes and seconds
                total_time_seconds = time.time() - start_time
                minutes = int(total_time_seconds // 60)
                remaining_seconds = total_time_seconds % 60
                st.write(f"Running Time: {minutes} minutes and {remaining_seconds: .2f} seconds") 

        else: 
            st.write("No file detected, please upload a file")

    except Exception as e:
        st.error("**The program is unusable for awhile. Please contact the author or try again after 2 days.**")
        logging.error(e, exc_info=True)

if __name__ == "__main__":
    configure_openai()
    main()