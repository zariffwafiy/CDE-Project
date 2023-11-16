import pickle
from models import LanguageNgramModel, MissingLetterModel
from abbreviation_spellchecker import noisy_channel

def load_and_apply_models(input_string, model_path):
    with open(model_path, 'rb') as model_file:
        big_lang_model, big_missing_model, all_letters = pickle.load(model_file)

    result = noisy_channel(input_string, big_lang_model, big_missing_model, max_attempts=1000, optimism=0.9, freedom=3.0, verbose=False)
    return result, big_lang_model, big_missing_model

if __name__ == "__main__":
    input_string = 'Ptro'
    model_path = "abbreviation_spellchecker.pkl"
    
    result, big_lang_model, big_missing_model = load_and_apply_models(input_string.lower(), model_path)
    
    # Use the loaded models or result as needed
    print(result)