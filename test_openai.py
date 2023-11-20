import re
import openai

openai.api_type = "azure"
openai.api_base = "https://openailx.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = "3be6ba13cc1f4a16bd5293d8feba2036"

# methodology for string comparison
# open ai
def openai_similarity(word1, word2):
    # openai
    try:
        # Construct a prompt for the specific input-reference pair
        prompt = f"Provide a precise semantic similarity score (0.xxxx) between '{word1}' and '{word2}'."
    
        # Call OpenAI API for this specific input-reference pair
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=20,
            temperature=0.2,
            n=1,
            stop=None,
            logprobs=0
        )

        # print(response)

        # Extract the similarity score using a regular expression
        similarity_score_match = re.search(r'(\d+\.\d+)', response.choices[0].text)

        if similarity_score_match:
            similarity_score = round(float(similarity_score_match.group(1)), 4)
            print(similarity_score)
        else:
            similarity_score = 0
            raise ValueError("No numeric similarity score found in the response.")
        return similarity_score
        

    except Exception as e:
        similarity_score = 0
        print(f"Exception in comparing '{word1}' with '{word2}': {str(e)}")
        return similarity_score
    
word1 = "enty key"
word2 = "entity key"
openai_similarity(word1, word2)
