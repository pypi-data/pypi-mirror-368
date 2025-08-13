from __future__ import annotations

import ipaddress
import re

from nltk import download
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


download('wordnet')
download('words')
download('punkt')
download('punkt_tab')

lemmatizer = WordNetLemmatizer()
common_words = {w.lower() for w in words.words()}


def is_common_word(token: str) -> bool:
    """
    >>> is_common_word("hello")
    True
    >>> is_common_word("world")
    True
    >>> is_common_word("worlds")
    True
    >>> is_common_word("dasjkdsbnajkdw")
    False
    """
    return lemmatizer.lemmatize(token.lower()) in common_words


def is_hex_digit(c: str) -> bool:
    return c in '0123456789abcdefABCDEF'


def is_hex_string(token: str) -> bool:
    """
    >>> is_hex_string("1234")
    True
    >>> is_hex_string("1234a")
    True
    >>> is_hex_string("1234A")
    True
    >>> is_hex_string("1234G")
    False
    """
    return all(is_hex_digit(c) for c in token)


def is_digit_string(token: str) -> bool:
    """
    >>> is_digit_string("1234")
    True
    >>> is_digit_string("1234a")
    False
    """
    return all(c.isdigit() for c in token)


def is_base64_string(token: str) -> bool:
    """
    >>> is_base64_string("1234")
    True
    >>> is_base64_string("1234a")
    True
    >>> is_base64_string("12dsahjldkjl1;d,.1")
    False
    """
    return all(c.isalnum() or c in '+/=' for c in token)


def is_punctuation(token: str) -> bool:
    """
    >>> is_punctuation("hello")
    False
    >>> is_punctuation("!")
    True
    >>> is_punctuation("-")
    True
    >>> is_punctuation("world!")
    False
    >>> is_punctuation("*&%$%^*()")
    True
    """
    import string

    return all(c in string.punctuation for c in token)


def is_uncommon_word(token: str) -> bool:
    return not is_common_word(token)


def is_random_string(token: str) -> bool:
    if (
        (re.search(r'\d', token) and len(token) > 2) or re.search(
            r'\W', token,
        ) or len(token) > 15
    ):
        return True
    return False


def need_mask(token: str) -> bool:
    """
    >>> need_mask("hello")
    False
    >>> need_mask("cf9849d0ca34c754cabf166dbc5c5080")
    True
    >>> need_mask("1234")
    True
    >>> need_mask("Nzg4ZTAxYTdiNDI2ZDg1MzM0MWJiODI0MzhhYzkxMTUgIC0K")
    True
    >>> need_mask("token")
    False
    """
    if is_common_word(token):
        return False
    if is_punctuation(token):
        return False
    if is_hex_string(token):
        return True
    if is_digit_string(token):
        return True
    if is_base64_string(token):
        return True
    if is_random_string(token):
        return True
    return False


def mask_word(word: str) -> str:
    mask = 'MASKED'
    return mask if is_random_string(word) else word


def mask_sentence(sentence: str, word_maskers=[mask_word]) -> str:
    """
    >>> mask_sentence("hello world")
    'hello world'
    >>> mask_sentence("cf9849d0ca34c754cabf166dbc5c5080")
    'MASKED'
    >>> mask_sentence("BunnyCDN - Node SG1-944")
    'BunnyCDN - Node MASKED'
    """
    masked_words = []
    for word in word_tokenize(sentence):
        if need_mask(word):
            masked_word = word
            for masker in word_maskers:
                masked_word = masker(masked_word)
            masked_words.append(masked_word)
        else:
            masked_words.append(word)
    return ' '.join(masked_words)


def mask_server(sentence: str) -> str:
    return sentence


def mask_header(
    header_name: str, header_value: str, word_maskers=[mask_word],
) -> tuple[str, str]:
    return header_name, mask_sentence(header_value, word_maskers=word_maskers)


def custom_server_masker(sentence: str) -> str:
    if sentence.startswith('BunnyCDN-'):
        return 'BunnyCDN-MASKED'
    return mask_server(sentence)


def custom_header_masker(
    header_name: str, header_value: str, word_maskers=[mask_word],
) -> tuple[str, str]:
    if header_name == 'X-Azion-Edge-Pop':
        return header_name, 'MASKED'
    if header_name == 'Host':
        return header_name, host_masker(header_value)
    return mask_header(header_name, header_value, word_maskers=word_maskers)


def host_masker(host: str) -> str:
    if is_ip_address(host):
        return ''
    return host


def is_ip_address(ip: str) -> bool:
    """Check if a string is a valid IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
