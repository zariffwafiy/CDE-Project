import re
import openai
import logging

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
    prompt = f"{definitions}\n{context}\nProvide a precise semantic similarity score (0.xxxx) between data attribute:'{word1}' and data element:'{word2}'.Justify the score in less than 30 words."
    
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
            max_tokens=100,
            temperature=0,
            n=1,
            stop=None,
            logprobs=0
        )

        if response and response.choices:
            result_text = response.choices[0].text

            # Extract the similarity score using a regular expression
            similarity_score_match = re.search(r'(\d+\.\d+)', result_text)
            similarity_score = round(float(similarity_score_match.group(1)), 4) if similarity_score_match else 0
        
            # Extract the justification
            justification_match = re.search(r'\.(.+)', result_text)
            justification = justification_match.group(1).strip() if justification_match else "No justification provided."
            
            logger.info(f"Similarity score: {similarity_score}")
            logger.info(f"Justification: {justification}")

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
    

# example usage
word1 = "Catalog Profile"
word2 = "Equipment's Catalog Profile"
nomalized_similarity = round((openai_similarity(word1, word2) + 1) / 2, 4)
logger.info(f"Normalized similarity: {nomalized_similarity}")

