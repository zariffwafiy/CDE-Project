from collections import defaultdict, Counter
import numpy as np
import pandas as pd


class LanguageNgramModel:
    """Language model based on n-grams."""
    def __init__(self, order=1, smoothing=1.0, recursive=0.001):
        self.order = order
        self.smoothing = smoothing
        self.recursive = recursive
        self.counter_ = defaultdict(Counter)
        self.unigrams_ = Counter()
        self.vocabulary_ = set()

    def fit(self, corpus):
        """Estimate counts on a text."""
        for i, token in enumerate(corpus[self.order:]):
            context = corpus[i:(i + self.order)]
            self.counter_[context][token] += 1
            self.unigrams_[token] += 1
            self.vocabulary_.add(token)
        self.vocabulary_ = sorted(list(self.vocabulary_))
        if self.recursive > 0 and self.order > 0:
            self.child_ = LanguageNgramModel(self.order - 1, self.smoothing, self.recursive)
            self.child_.fit(corpus)

    def get_counts(self, context):
        """Get smoothed count of each letter appearing after context."""
        if self.order:
            local = context[-self.order:]
        else:
            local = ''
        freq_dict = self.counter_[local]
        freq = pd.Series(index=self.vocabulary_)
        for i, token in enumerate(self.vocabulary_):
            freq[token] = freq_dict[token] + self.smoothing
        if self.recursive > 0 and self.order > 0:
            child_freq = self.child_.get_counts(context) * self.recursive
            freq += child_freq
        return freq

    def predict_proba(self, context):
        """Get smoothed probability of each letter appearing after context."""
        counts = self.get_counts(context)
        return counts / counts.sum()

    def single_log_proba(self, context, continuation):
        """Estimate log-probability that context is followed by continuation."""
        result = 0.0
        for token in continuation:
            result += np.log(self.predict_proba(context)[token])
            context += token
        return result

    def single_proba(self, context, continuation):
        """Estimate probability that context is followed by continuation."""
        return np.exp(self.single_log_proba(context, continuation))

class MissingLetterModel:
    """Model to predict missing letters."""
    def __init__(self, order=0, smoothing_missed=0.3, smoothing_total=1.0):
        self.order = order
        self.smoothing_missed = smoothing_missed
        self.smoothing_total = smoothing_total
        self.missed_counter_ = defaultdict(Counter)
        self.total_counter_ = defaultdict(Counter)

    def fit(self, sentence_pairs):
        """Estimate counts for missing letters."""
        for (original, observed) in sentence_pairs:
            for i, (original_letter, observed_letter) in enumerate(zip(original[self.order:], observed[self.order:])):
                context = original[i:(i + self.order)]
                if observed_letter == '-':
                    self.missed_counter_[context][original_letter] += 1
                self.total_counter_[context][original_letter] += 1

    def predict_proba(self, context, last_letter):
        """Estimate probability that last_letter after context is missed."""
        if self.order:
            local = context[-self.order:]
        else:
            local = ''
        missed_freq = self.missed_counter_[local][last_letter] + self.smoothing_missed
        total_freq = self.total_counter_[local][last_letter] + self.smoothing_total
        return missed_freq / total_freq

    def single_log_proba(self, context, continuation, actual=None):
        """Estimate log-probability of continuaton being distorted to actual after context. 
        If actual is None, assume no distortion
        """
        if not actual:
            actual = continuation
        result = 0.0
        for orig_token, act_token in zip(continuation, actual):
            pp = self.predict_proba(context, orig_token)
            if act_token == '-':
                pp = 1 - pp
            result += np.log(pp)
            context += orig_token
        return result

    def single_proba(self, context, continuation, actual=None):
        """Estimate probability of continuaton being distorted to actual after context. 
        If actual is None, assume no distortion
        """
        return np.exp(self.single_log_proba(context, continuation, actual))
