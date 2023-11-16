from models import LanguageNgramModel, MissingLetterModel
import numpy as np
from heapq import heappush, heappop
import pickle
import re

def generate_options(prefix_proba, prefix, suffix, lang_model, missed_model, optimism=0.5, cache=None):
    """Generate options for the next letter in a sequence."""
    options = []
    for letter in lang_model.vocabulary_ + ['']:
        if letter:  # Assume a missing letter
            next_letter = letter
            new_suffix = suffix
            new_prefix = prefix + next_letter
            proba_missing_state = - np.log(missed_model.predict_proba(prefix, letter))
        else:  # Assume no missing letter
            next_letter = suffix[0]
            new_suffix = suffix[1:]
            new_prefix = prefix + next_letter
            proba_missing_state = - np.log((1 - missed_model.predict_proba(prefix, next_letter)))
        proba_next_letter = - np.log(lang_model.single_proba(prefix, next_letter))
        if cache:
            proba_suffix = cache[len(new_suffix)] * optimism
        else:
            proba_suffix = - np.log(lang_model.single_proba(new_prefix, new_suffix)) * optimism
        proba = prefix_proba + proba_next_letter + proba_missing_state + proba_suffix
        options.append((proba, new_prefix, new_suffix, letter, proba_suffix))
    return options


def noisy_channel(word, lang_model, missed_model, freedom=1.0, max_attempts=1000, optimism=0.1, verbose=True):
    """Noisy channel model for spelling correction."""
    query = word + ' '
    prefix = ' '
    prefix_proba = 0.0
    suffix = query
    full_origin_logprob = -lang_model.single_log_proba(prefix, query)
    no_missing_logprob = -missed_model.single_log_proba(prefix, query)
    best_logprob = full_origin_logprob + no_missing_logprob

    heap = [(best_logprob * optimism, prefix, suffix, '', best_logprob * optimism)]
    candidates = [(best_logprob, prefix + query, '', None, 0.0)]

    if verbose:
        print('Baseline score is', best_logprob)

    cache = {}
    for i in range(len(query) + 1):
        future_suffix = query[:i]
        cache[len(future_suffix)] = -lang_model.single_log_proba('', future_suffix)  # Rough approximation
        cache[len(future_suffix)] += -missed_model.single_log_proba('', future_suffix)  # Add missingness

    for i in range(max_attempts):
        if not heap:
            break
        next_best = heappop(heap)
        if verbose:
            print(next_best)
        if next_best[2] == '':  # It is a leaf
            if next_best[0] <= best_logprob + freedom:
                candidates.append(next_best)
                if next_best[0] < best_logprob:
                    best_logprob = next_best[0]
        else:  # It is not a leaf - generate more options
            prefix_proba = next_best[0] - next_best[4]
            prefix = next_best[1]
            suffix = next_best[2]
            new_options = generate_options(prefix_proba, prefix, suffix, lang_model, missed_model, optimism, cache)
            for new_option in new_options:
                if new_option[0] < best_logprob + freedom:
                    heappush(heap, new_option)

    if verbose:
        print('Heap size is', len(heap), 'after', i, 'iterations')

    """
    result = {}
    for candidate in candidates:
        if candidate[0] <= best_logprob + freedom:
            result[candidate[1][1:-1]] = candidate[0]
    """

    most_probable = min(candidates, key = lambda x: x[0])

    return most_probable[1][1:-1]


def train_and_save_models(corpus_path, save_path):

    
    with open(corpus_path, encoding='utf-8') as f:
        text = f.read()

    text2 = re.sub(r'[^a-z ]+', '', text.lower().replace('\n', ' '))

    all_letters = ''.join(sorted(set(text2)))

    missing_set = [
    ] + [(all_letters, '-' * len(all_letters))] * 3 + [(all_letters, all_letters)] * 10 + [('aeiouy', '------')] * 30

    big_lang_model = LanguageNgramModel(4, 0.001, 0.01)
    big_lang_model.fit(text2)

    big_missing_model = MissingLetterModel(0, 0.1)
    big_missing_model.fit(missing_set)

    with open(save_path, 'wb') as model_file:
        pickle.dump((big_lang_model, big_missing_model, all_letters), model_file)