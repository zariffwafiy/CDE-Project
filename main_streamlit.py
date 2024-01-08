import re
import pandas as pd
import openai
import logging
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import time
from PIL import Image

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

    # set page configuration 
    st.set_page_config(
        page_title="CDE Advisor: Semantic Similarity Comparison",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )  

    # HTML and CSS for setting background image and additional styles
    background_html = """
    <style>
        body {
            background-image: url('assets/petronas.jpg');
            background-size: cover;
            background-color: #00A160; /* Background color */
            font-family: 'Arial', sans-serif; /* Font family */
            color: #00A160; /* Text color */
            padding: 20px; /* Padding for content */
        }

        h1 {
            color: #00A160; /* Header text color */
            text-align: center; /* Center-align header text */
        }

        p {
            font-size: 18px; /* Font size for paragraphs */
            line-height: 1.6; /* Line height for paragraphs */
            color: #9be5c0;
        }

        .stApp {
            color: #00A160; /* Text color for the entire app */
        }

        /* Add more styles as needed */

    </style>
    """
    # Display the HTML with the background image
    st.markdown(background_html, unsafe_allow_html=True)
 
    logo_image = "assets/petronas 4.png"

    # Add sidebar for documentation  
    st.sidebar.image(logo_image, width = 200)
    st.sidebar.header("About")
    st.sidebar.markdown("This is a simple prototype to compare the semantic similarity between a data attribute in a data dictionary and a data element in a data standard.")
    st.sidebar.header("How to Use")
    st.sidebar.markdown("Please filter out the domain of the data dictionary and enter the data attribute/ data attribute description in the text area below.")
    st.sidebar.markdown("The semantic similarity score and glossary will be displayed on the below each corresponding data element.")
    st.sidebar.divider()
    st.sidebar.info("**Data Scientist: [@zariffwafiy](https://github.com/zariffwafiy)**", icon="🧠")

    
    st.title("📖CDE Advisor: Semantic Similarity Comparison")
    # Load your standard
    standard = pd.read_csv("data/PETRONAS Data Standard - All -  July 2023.csv")

    # dictionary to store minutes for each domain
    minutes_per_category = {
        "Civil / Structure & Pipeline Engineering": 3, 
        "Electrical Engineering": 6, 
        "Mechanical Engineering": 14, 
        "Physical Asset Management": 1, 
        "Materials, Corrosion & Inspection Engineering": 4, 
        "Process Engineering": 10, 
        "Drilling": 3, 
        "Petroleum Engineering": 7, 
        "Geoscience": 8, 
        "Project Management": 4, 
        "Marketing & Trading": 2
    }

    # Calculate total minutes for "All"
    total_minutes_all = sum(minutes_per_category.values())

    filter_standard_options_with_minutes = [f"{option} ({minutes} mins)" for option, minutes in minutes_per_category.items()]
    filter_standard_options_with_minutes.append(f"All ({total_minutes_all} mins)")

    # Create a dropdown for the user to choose from multiple values
    filter_standard = st.selectbox("**Choose Data Domain**", filter_standard_options_with_minutes, index= len(filter_standard_options_with_minutes)-1)

    # Apply the condition
    if "All (62 mins)" in filter_standard:
        standard_filtered = standard
    else:
        # Get the first part before "("
        selected_category = filter_standard.split("(")[0].strip()

        # Filter the dataframe based on the selected category
        standard_filtered = standard[standard["DATA DOMAIN"].str.strip() == selected_category].reset_index(drop=True)


    field_description = st.text_area("**Enter Data Attribute/ Data Attribute Description:**")

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
        print(standard_filtered)
        st.header("Top 3 Matches:")

        start_time = time.time()

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers = 3) as executor:
            # Use the executor to process each data element concurrently
            scores = list(executor.map(lambda x: openai_similarity(field_description, x[0], x[1]), element_glossary_pairs))

        # Sort the scores in descending order based on the inner tuple's second element
        sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)

        # Display the top 3 highest scored comparisons and their corresponding data elements
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