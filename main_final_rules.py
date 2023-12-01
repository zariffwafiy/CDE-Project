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

def remove_duplicates(df, column_name):
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

    # load and read csv for both data dictionary and data standard
    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    data1 = pd.read_csv(data1_path)

    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv" 
    data2 = pd.read_csv(data2_path)

    # use remove duplicates
    column_to_check = "FIELD NAME/DATA ATTRIBUTE(S)"
    # data1 = remove_duplicates(data1, column_to_check)
    # print(data1)
    print("-----")
    # filter out relevant values for data dictionary
    filter_data1 = [ "MI_EQUIP000_CAT_PROF_C", "CC_EQUIP000_TUBE_MX_IN_PRES_N", "CC_EQUIP000_TUBE_MX_OUT_PRES_N", "CC_EQUIP000_TUBE_OPR_IN_PRES_N", "CC_EQUIP000_TUBE_OPR_OU_PRES_N"]
    data1 = data1.drop_duplicates(subset="FIELD NAME/DATA ATTRIBUTE(S)").loc[data1["FIELD NAME/DATA ATTRIBUTE(S)"].isin(filter_data1)]

    # filter out relevant data domain for data standard
    filter_data2 = data1["DATA DOMAIN "].iloc[0]
    data2 = data2[data2["DATA DOMAIN"].isin([filter_data2])].reset_index(drop=True)

    # list to store data1 values
    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()

    # prepare result dataframe 1 (table_name_vs_data_entity)
    sheet_df_1 = pd.DataFrame(columns=["DATA ENTITY"])
    sheet_df_1["DATA ENTITY"] = data2["DATA ENTITY"]

    # prepare result dataframe 2 (table_name_vs_glossary)
    sheet_df_2 = pd.DataFrame(columns=["BUSINESS DEFINITION/ GLOSSARY"])
    sheet_df_2["BUSINESS DEFINITION/ GLOSSARY"] = data2["BUSINESS DEFINITION/ GLOSSARY"]

    # prepare result dataframe 3 (table_desc_vs_data_element)
    sheet_df_3 = pd.DataFrame(columns=["DATA ELEMENT"])
    sheet_df_3["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # prepare result dataframe 4 (table_desc_vs_glossary)
    sheet_df_4 = pd.DataFrame(columns=["BUSINESS DEFINITION/ GLOSSARY"])
    sheet_df_4["BUSINESS DEFINITION/ GLOSSARY"] = data2["BUSINESS DEFINITION/ GLOSSARY"]

    # prepare result dataframe 5 (field_name_vs_data_entity)
    sheet_df_5 = pd.DataFrame(columns=["DATA ENTITY"])
    sheet_df_5["DATA ENTITY"] = data2["DATA ENTITY"]

    # prepare result dataframe 6 (field_name_vs_glossary)
    sheet_df_6 = pd.DataFrame(columns=["BUSINESS DEFINITION/ GLOSSARY"])
    sheet_df_6["BUSINESS DEFINITION/ GLOSSARY"] = data2["BUSINESS DEFINITION/ GLOSSARY"]

    # prepare result dataframe 7 (field_desc_vs_data_element)
    sheet_df_7 = pd.DataFrame(columns=["DATA ELEMENT"])
    sheet_df_7["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # prepare result dataframe 8 (field_desc_vs_glossary)
    sheet_df_8 = pd.DataFrame(columns=["BUSINESS DEFINITION/ GLOSSARY"])
    sheet_df_8["BUSINESS DEFINITION/ GLOSSARY"] = data2["BUSINESS DEFINITION/ GLOSSARY"]

    sheet_df_9 = pd.DataFrame(columns=["DATA ELEMENT"])
    sheet_df_9["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # preprocess data dictionary
    preprocess_data(data1)

    # loop for applying comparison
    output_path = "results/result_openai_filtervalue_specdomain.xlsx"
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for table_name, table_desc, field_name, field_desc, original_name in zip(
            data1["TABLE NAME"],
            data1["TABLE DESCRIPTION/SUB FOLDER NAME "],
            data1["FIELD NAME/DATA ATTRIBUTE(S)"], 
            data1["FIELD DESCRIPTION"],
            data1_names
            ):

            # Compare 1. table_name_vs_data_entity
            sheet_name_1 = "table_name_vs_data_entity"
            sheet_df_1[original_name] = data2["DATA ELEMENT"].apply(
                lambda data_element: round(openai_similarity(table_name, data_element), 4)
            )

            # Compare 2. table_name vs data_glossary
            sheet_name_2 = "table_name_vs_glossary"
            sheet_df_2[original_name] = data2["BUSINESS DEFINITION/ GLOSSARY"].apply(
                lambda glossary: round(openai_similarity(table_name, glossary), 4)
            )

            # Compare 3. table_desc_vs_data_element
            sheet_name_3 = "table_desc_vs_data_element"
            sheet_df_3[original_name] = data2["DATA ELEMENT"].apply(
                lambda data_element: round(openai_similarity(table_desc, data_element), 4)
            )

            # Compare 4. table_desc_vs_glossary
            sheet_name_4 = "table_desc_vs_glossary"
            sheet_df_4[original_name] = data2["BUSINESS DEFINITION/ GLOSSARY"].apply(
                lambda glossary: round(openai_similarity(table_desc, glossary), 4)
            )

            # Compare 5. field_name_vs_data_entity
            sheet_name_5 = "field_name_vs_data_entity"
            sheet_df_5[original_name] = data2["DATA ENTITY"].apply(
                lambda data_entity: round(openai_similarity(field_name, data_entity), 4)
            )

            # Compare 6. field_name_vs_glossary
            sheet_name_6 = "field_name_vs_glossary"
            sheet_df_6[original_name] = data2["BUSINESS DEFINITION/ GLOSSARY"].apply(
                lambda glossary: round(openai_similarity(field_name, glossary), 4)
            )

            # Compare 7. field_desc_vs_data_element
            sheet_name_7 = "field_desc_vs_data_element"
            sheet_df_7[original_name] = data2["DATA ELEMENT"].apply(
                lambda data_element: round(openai_similarity(field_desc, data_element), 4)
            )

            # Compare 8. field_desc_vs_glossary
            sheet_name_8 = "field_desc_vs_glossary"
            sheet_df_8[original_name] = data2["BUSINESS DEFINITION/ GLOSSARY"].apply(
                lambda glossary: round(openai_similarity(field_desc, glossary), 4)
            )

            # combination of scores (average of all scores)
            sheet_name_9 = "score_combination"
            sheet_df_9[original_name] = round((sheet_df_3[original_name] + sheet_df_4[original_name] + sheet_df_5[original_name] + sheet_df_6[original_name] + sheet_df_7[original_name] + sheet_df_8[original_name]) / 8, 4)


        # Save the sheets to Excel
        sheet_df_1.to_excel(writer, sheet_name=sheet_name_1, index=False)
        sheet_df_2.to_excel(writer, sheet_name=sheet_name_2, index=False)
        sheet_df_3.to_excel(writer, sheet_name=sheet_name_3, index=False)
        sheet_df_4.to_excel(writer, sheet_name=sheet_name_4, index=False)
        sheet_df_5.to_excel(writer, sheet_name=sheet_name_5, index=False)
        sheet_df_6.to_excel(writer, sheet_name=sheet_name_6, index=False)
        sheet_df_7.to_excel(writer, sheet_name=sheet_name_7, index=False)
        sheet_df_8.to_excel(writer, sheet_name=sheet_name_8, index=False)
        sheet_df_9.to_excel(writer, sheet_name=sheet_name_9, index=False)

if __name__ == "__main__":
    main()
