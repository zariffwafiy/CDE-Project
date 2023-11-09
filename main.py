import pandas as pd

# methodology for string comparison
def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    result = intersection / union if union != 0 else 0
    return result 

def main():
    # Data dictionary
    data1_path = "data/Data Document PRPC Track2- GE APM Ver.01 - zarif.csv"
    data2_path = "data/PETRONAS Data Standard - All -  July 2023.csv" 

    data1 = pd.read_csv(data1_path)
    data2 = pd.read_csv(data2_path)

    # Prepare result_df 
    domains = data1["DATA DOMAIN "].iloc[0]
    data2 = data2[data2["DATA DOMAIN"].isin([domains])].reset_index(drop=True)

    data1_names = data1["FIELD NAME/DATA ATTRIBUTE(S)"].tolist()
    result_df = pd.DataFrame(columns=["DATA ELEMENT"])
    result_df["DATA ELEMENT"] = data2["DATA ELEMENT"]

    # Preprocess data
    data1["FIELD NAME/DATA ATTRIBUTE(S)"] = data1["FIELD NAME/DATA ATTRIBUTE(S)"].str.lower().str.replace(r'[^a-zA-Z\s]', '', regex=True)
    data2["DATA ELEMENT"] = data2["DATA ELEMENT"].str.lower().str.replace(r'[^a-zA-Z\s]', '', regex=True)

    for set1,original_name in zip(data1["FIELD NAME/DATA ATTRIBUTE(S)"], data1_names):
        result_df[original_name] = data2["DATA ELEMENT"].apply(lambda set2: round(jaccard_similarity(set(set1), set(set2)), 4))
    
    result_df.to_csv("result1.csv", encoding="utf-8", index=False)

if __name__ == "__main__":
    main()
