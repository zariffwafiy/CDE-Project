import re
import pandas as pd
import openai

def configure_openai():
    openai.api_type = "azure"
    openai.api_base = "https://openailx.openai.azure.com/"
    openai.api_version = "2022-12-01"
    openai.api_key = "3be6ba13cc1f4a16bd5293d8feba2036"

def openai_similarity(word1, word2):
    try:
        print(f"word1: {word1}")
        print(f"word2: {word2}")
        prompt = f"Provide a precise semantic similarity score (0.xxxx) between '{word1}' and '{word2}'."
    
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=50, 
            temperature=0.2,
            n=1,
            stop=None,
            logprobs=0
        )

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

def preprocess_data(data):
    data["FIELD NAME/DATA ATTRIBUTE(S)"] = data["FIELD NAME/DATA ATTRIBUTE(S)"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["FIELD DESCRIPTION"] = data["FIELD DESCRIPTION"].str.replace(r'System generated field:', '', case=False, regex=True) # only for field description
    data["FIELD DESCRIPTION"] = data["FIELD DESCRIPTION"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["TABLE NAME"] = data["TABLE NAME"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["TABLE DESCRIPTION/SUB FOLDER NAME "] = data["TABLE DESCRIPTION/SUB FOLDER NAME "].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)

def main():
    configure_openai()

    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    data1 = pd.read_csv(data1_path)

    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv" 
    data2 = pd.read_csv(data2_path)

    domains = data1["DATA DOMAIN "].iloc[0]
    data2 = data2[data2["DATA DOMAIN"].isin([domains])].reset_index(drop=True)

    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()

    result_df = pd.DataFrame(columns=["DATA ELEMENT"])
    result_df["DATA ELEMENT"] = data2["DATA ELEMENT"]

    preprocess_data(data1)

    for field_name, field_description, table_name, table_description, data_element, original_name in zip(
            data1["FIELD NAME/DATA ATTRIBUTE(S)"], data1["FIELD DESCRIPTION"], data1["TABLE NAME"],
            data1["TABLE DESCRIPTION/SUB FOLDER NAME "], data2["DATA ELEMENT"], data1_names
        ):
        result_df[original_name] = data2["DATA ELEMENT"].apply(
            lambda data_element: round(openai_similarity(field_description, data_element), 4)
        )

    output_path = "results/result_openai_complete_domain.csv"
    result_df.to_csv(output_path, encoding="utf-8", index=False)

if __name__ == "__main__":
    main()
