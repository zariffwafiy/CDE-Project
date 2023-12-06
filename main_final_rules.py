import re
import pandas as pd
import openai
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='log_file.txt', 
    filemode='w',
    format='%(asctime)s - %(message)s'
)

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
        print(f"word: {word1}")
        print(f"word: {word2}")

        # prompt = definitions
        # context = "I am comparing the semantic similarity between a data attribute in a data dictionary and a data element in a data standard."
        prompt = f"\n. Provide a precise semantic similarity score (0.xxxx) between '{word1}' and '{word2}'."
    
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

    # reset index of new dataframe
    df_unique = df_unique.reset_index(drop=True)

    return df_unique

def preprocess_data(data):
    data["FIELD NAME/DATA ATTRIBUTE(S)"] = data["FIELD NAME/DATA ATTRIBUTE(S)"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["FIELD DESCRIPTION"] = data["FIELD DESCRIPTION"].str.replace(r'System generated field:', '', case=False, regex=True) # only for field desc
    data["FIELD DESCRIPTION"] = data["FIELD DESCRIPTION"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["TABLE NAME"] = data["TABLE NAME"].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    data["TABLE DESCRIPTION/SUB FOLDER NAME "] = data["TABLE DESCRIPTION/SUB FOLDER NAME "].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True)

definitions = (
    "Data Attribute - It is at the lowest level of data taxonomy in a data dictionary and received from clients/businesses.\n"
    "Data Dictionary - It is a collection of data attributes.\n"
    "Data Element - It is at the lowest level of data taxonomy in a data standard and .\n"
    "Data Standard - It is a collection of data elements that is used by analyst.\n"
)

def main():

    configure_openai()

    # load and read csv for both data dictionary and data standard
    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    data1 = pd.read_csv(data1_path)

    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv" 
    data2 = pd.read_csv(data2_path)

    # use remove duplicates
    # column_to_check = "FIELD NAME/DATA ATTRIBUTE(S)"
    # remove duplicate if necessary
    # data1 = remove_duplicates(data1, column_to_check)
    
    # filter out relevant values for data dictionary
    filter_data1 = [ "MI_EQUIP000_CAT_PROF_C"]
    data1 = data1.drop_duplicates(subset="FIELD NAME/DATA ATTRIBUTE(S)").loc[data1["FIELD NAME/DATA ATTRIBUTE(S)"].isin(filter_data1)]

    # filter out relevant data domain for data standard
    filter_data2 = data1["DATA DOMAIN "].iloc[0]
    data2 = data2[data2["DATA DOMAIN"].isin([filter_data2])].reset_index(drop=True)

    # list to store data1 values
    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()

    # prepare result dataframe 7 (field_desc_vs_data_element)
    sheet_df_1 = pd.DataFrame(columns=["DATA ELEMENT"])
    sheet_df_1["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # prepare result dataframe 8 (field_desc_vs_glossary)
    sheet_df_2 = pd.DataFrame(columns=["BUSINESS DEFINITION/ GLOSSARY"])
    sheet_df_2["BUSINESS DEFINITION/ GLOSSARY"] = data2["BUSINESS DEFINITION/ GLOSSARY"]
    
    # Create a combination score sheet
    sheet_df_comb = pd.DataFrame(columns=["DATA ELEMENT"])
    sheet_df_comb["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # Create a summary sheet
    summary_sheet = pd.DataFrame(columns=["DATA ATTRIBUTE", "Top Match 1", "Score 1", "Glossary 1", "Entity 1", "Top Match 2", "Score 2", "Glossary 2", "Entity 2", "Top Match 3", "Score 3", "Glossary 3", "Entity 3"])

    # preprocess data dictionary
    preprocess_data(data1)

    # loop for applying comparison
    output_path = "results/result_openai_filtervalue_specdomain.xlsx"
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for field_desc, original_name in zip(
            data1["FIELD DESCRIPTION"],
            data1_names
            ):

            # Compare field_desc_vs_data_element
            sheet_name_1 = "field_desc_vs_data_element"
            sheet_df_1[original_name] = data2["DATA ELEMENT"].apply(
                lambda data_element: round(openai_similarity(field_desc, data_element), 4)
            )

            # Compare field_desc_vs_glossary
            sheet_name_2 = "field_desc_vs_glossary"
            sheet_df_2[original_name] = data2["BUSINESS DEFINITION/ GLOSSARY"].apply(
                lambda glossary: round(openai_similarity(field_desc, glossary), 4)
            )

            # combination of scores (average of all scores)
            sheet_name_comb = "score_combination"
            sheet_df_comb[original_name] = round((sheet_df_1[original_name] + sheet_df_2[original_name]) / 2, 4)
            
            # find top 3 data elements with the highest score
            top_matches = sheet_df_comb[original_name].nlargest(3).index.tolist()
            top_scores = sheet_df_comb[original_name].nlargest(3).tolist()

            # Get corresponding glossary and data entity values
            top_glossary_values = data2.loc[top_matches, "BUSINESS DEFINITION/ GLOSSARY"].tolist()
            top_data_entity_values = data2.loc[top_matches, "DATA ELEMENT"].tolist()

            # Create a summary sheet
            sheet_name_summary = "summary"
            summary_df = pd.DataFrame({
                "DATA ATTRIBUTE": original_name,
                "Top Match 1": data2.loc[top_matches[0], "DATA ELEMENT"],
                "Score 1": top_scores[0],
                "Glossary 1": top_glossary_values[0],
                "Entity 1": top_data_entity_values[0],
                "Top Match 2": data2.loc[top_matches[1], "DATA ELEMENT"],
                "Score 2": top_scores[1],
                "Glossary 2": top_glossary_values[1],
                "Entity 2": top_data_entity_values[1],
                "Top Match 3": data2.loc[top_matches[2], "DATA ELEMENT"],
                "Score 3": top_scores[2],
                "Glossary 3": top_glossary_values[2],
                "Entity 3": top_data_entity_values[2],
            }, index=[0])

        summary_sheet = pd.concat([summary_sheet, summary_df], ignore_index=True)

        # Save the sheets to Excel
        sheet_df_1.to_excel(writer, sheet_name=sheet_name_1, index=False)
        sheet_df_2.to_excel(writer, sheet_name=sheet_name_2, index=False)
        sheet_df_comb.to_excel(writer, sheet_name=sheet_name_comb, index=False)
        summary_sheet.to_excel(writer, sheet_name=sheet_name_summary, index=False)

if __name__ == "__main__":
    main()
