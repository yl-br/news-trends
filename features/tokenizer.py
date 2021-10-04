import string
import re


def tokenize(text, hebrew_stop_words):
    if text is None:
        return []
    text = text.replace('_', ' ')
    text = text.replace('-', ' ')
    text = text.replace('–', ' ')
    text = text.replace('־', ' ')
    text = text.replace('’', '')
    text = text.replace('״', '')
    text = text.replace('&quot;', '')
    text = text.replace('&amp;', '')
    text = text.replace('&#39;', '')


    only_text = text.translate(str.maketrans('', '', string.punctuation + string.digits))
    # title = title.replace('&quot;', '"')
    # punctuations = string.punctuation.replace('"', '')
    # only_text = title.translate(str.maketrans('', '', punctuations))
    # tokens = [re.sub(r'^"|"$', '',t) for t in only_text.split()] # Removes quote only if its the beginning or ending of the word.
    tokens = [t for t in only_text.split() if t if re.match(r"[א-ת]+", t) and t not in hebrew_stop_words and len(t) > 1]
    return tokens


def get_possibly_prefixed_words_striped_list(tokens):
    hebrew_initials_letters = ['ו','ש', 'כ', 'ל', 'ה', 'מ', 'ב']
    out_striped_words_list = [word[1:] for word in tokens if len(word) > 3 and word[0] in hebrew_initials_letters]
    return out_striped_words_list
