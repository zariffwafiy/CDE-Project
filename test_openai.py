import openai
import re

openai.api_type = "azure"
openai.api_base = "https://ptsg5edhopenai01.openai.azure.com/"
openai.api_version = "2023-09-15-preview"
openai.api_key = "d929ffb032eb4ef186804b69cbb95531"

MAX_TOKENS = 15
TEMPERATURE = 0
NUM_COMPLETIONS = 1

def openai_similarity(word1, word2):
    try:
        context = "I am comparing the semantic similarity between a data attribute in a data dictionary and a data element in a data standard."
        prompt = f"{context}\nProvide a semantic similarity score (0.xxxx) between data attribute:'{word1}' and data element:'{word2}' ."
    
        response = openai.Completion.create(
            engine='CDE-Advisor',
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

            print(f"word1: {word1}")
            print(f"word2: {word2}")
            print(f"Similarity score: {similarity_score}")
            print(f"Justification: {justification}")

            return word1, word2, similarity_score

        else:
            return word1, word2, 0, "Error in API response"

    except ValueError as ve:
        return word1, word2, 0, str(ve)

    except Exception as e:
        return word1, word2, 0, str(e)

print(openai_similarity("enty", "entity"))