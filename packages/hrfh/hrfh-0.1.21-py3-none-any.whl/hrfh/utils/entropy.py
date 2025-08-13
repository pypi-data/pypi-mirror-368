from __future__ import annotations

import math
from collections import Counter

from hrfh.utils.masker import is_common_word


def shannon_char_entropy(data: str):
    return shannon_ngram_entropy(data, n=1)


def normalized_shannon_entropy(data: str):
    return shannon_char_entropy(data) / math.log(len(data), 2)


def shannon_ngram_entropy(word: str, n: int):
    ngrams = [word[i: i + n] for i in range(len(word) - n + 1)]
    freq = Counter(ngrams)
    total_ngrams = len(ngrams)
    return -sum(
        (count / total_ngrams) * math.log2(count / total_ngrams)
        for count in freq.values()
    )


def is_gibberish(token: str, n: int = 2, entropy_threshold: int = 3):
    """
    >>> is_gibberish("apple")
    False
    >>> is_gibberish("apples")
    False
    >>> is_gibberish("applicable")
    False
    >>> is_gibberish("f638055d-afea-4249-bea7-c73b2a4fec5f")
    True
    >>> is_gibberish("ecea031b74f3e08cef1fba8765196145")
    True
    """
    if is_common_word(token):
        return False
    entropy = shannon_ngram_entropy(token, n)
    return entropy > entropy_threshold
