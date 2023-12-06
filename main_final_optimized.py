import re
import pandas as pd
import openai

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

def openai_similarity(word1, word2):
    """
    Calculates the semantic similarity score between two words using the OpenAI API.

    Args:
        word1 (str): The first word to compare.
        word2 (str): The second word to compare.

    Returns:
        float: The semantic similarity score between word1 and word2, ranging from 0 to 1.
    """
    try:
        print(f"word1: {word1}")
        print(f"word2: {word2}")
        prompt = f"Provide a precise semantic similarity score (0.xxxx) between '{word1}' and '{word2}'."
    
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=50, 
            temperature=0.2, # can adjust freedom/sensitivity
            n=1,
            stop=None,
            logprobs=0
        )

        logprobs = response['choices'][0]['logprobs']

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

def remove_duplicates(df, column_name):
    """
    Removes duplicates from a dataframe based on a specified column.

    Parameters:
        df (pandas.DataFrame): The input dataframe.
        column_name (str): The name of the column to check for duplicates.

    Returns:
        pandas.DataFrame: A new dataframe with duplicates removed.

    Raises:
        None

    Example usage:
        df = pd.DataFrame(...)
        result = remove_duplicates(df, 'column_name')
    """
    # check if column exists in dataframe
    # df = pd.DataFrame(df)
    if column_name not in df.columns:
        print(f"Column '{column_name}' does not exist in the dataframe")
        return
    
    # drop all occurence of duplciates in the specified column
    df_unique = df.drop_duplicates(subset = column_name, keep = True)

    # print the rows that are being removed
    # removed_rows = df[df.duplicated(subset=column_name, keep=False)]
    # print(f"Removed rows: \n{removed_rows}\n")

    # reset index of new dataframe
    df_unique = df_unique.reset_index(drop=True)

    return df_unique

def preprocess_data(data):
    data["FIELD NAME/DATA ATTRIBUTE(S)"] = data["FIELD NAME/DATA ATTRIBUTE(S)"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["FIELD DESCRIPTION"] = data["FIELD DESCRIPTION"].str.replace(r'System generated field:', '', case=False, regex=True) # only for field desc
    data["FIELD DESCRIPTION"] = data["FIELD DESCRIPTION"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["TABLE NAME"] = data["TABLE NAME"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["TABLE DESCRIPTION/SUB FOLDER NAME "] = data["TABLE DESCRIPTION/SUB FOLDER NAME "].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)

def main():
    configure_openai()

    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv"

    data1 = pd.read_csv(data1_path)
    data2 = pd.read_csv(data2_path)

    column_to_check = "FIELD NAME/DATA ATTRIBUTE(S)"
    # Define the list of values to filter from "FIELD NAME/DATA ATTRIBUTE(S)" column
    filter_data1 = [
        "MI_EQUIP000_CAT_PROF_C",
        "CC_EQUIP000_TUBE_MX_IN_PRES_N",
        "CC_EQUIP000_TUBE_MX_OUT_PRES_N",
        "CC_EQUIP000_TUBE_OPR_IN_PRES_N",
        "CC_EQUIP000_TUBE_OPR_OU_PRES_N"
    ]

    data1 = data1.drop_duplicates(subset=column_to_check).loc[data1[column_to_check].isin(filter_data1)]

    filter_data2 = data1["DATA DOMAIN "].iloc[0]
    data2 = data2[data2["DATA DOMAIN"].isin([filter_data2])].reset_index(drop=True).head(2)

    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()

    sheet_df = pd.DataFrame(columns=["DATA ELEMENT", "BUSINESS DEFINITION/ GLOSSARY"])

    preprocess_data(data1)

    output_path = "results/result_openai_filtervalue_specdomain_optimized.xlsx"
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for field_name, field_desc, original_name in zip(
            data1["FIELD NAME/DATA ATTRIBUTE(S)"],
            data1["FIELD DESCRIPTION"],
            data1_names
        ):
            for comparison_type, column_name in [
                ("DATA ELEMENT", "field_name_vs_data_entity"),
                ("BUSINESS DEFINITION/ GLOSSARY", "field_name_vs_glossary"),
                ("DATA ELEMENT", "field_desc_vs_data_element"),
                ("BUSINESS DEFINITION/ GLOSSARY", "field_desc_vs_glossary"),
                ("", "score_combination")
            ]:
                if comparison_type:
                    sheet_df[comparison_type] = data2[comparison_type].apply(
                        lambda x: round(openai_similarity(field_name if "field_name" in column_name else field_desc, x), 4)
                    )
                else:
                    sheet_df[original_name] = round(sheet_df.mean(axis=1), 4)

            sheet_df.to_excel(writer, sheet_name=column_name, index=False)


if __name__ == "__main__":
    main()
