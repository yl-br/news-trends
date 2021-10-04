import re
def clean_text(text):
    if text is None:
        return ''

    text = text.replace('_', ' ')
    text = text.replace('-', ' ')
    text = text.replace('–', ' ')
    text = text.replace('־', ' ')
    text = text.replace('"', '')
    text = text.replace('״', '')
    text = text.replace('’', '')
    text = text.replace("'", '')
    text = text.replace('&quot;', '')
    text = text.replace('&amp;', '')
    text = text.replace('&#39;', '')
    return text


def find_snippets(text, term, limit = 1):
    out_snippets = []
    for match in re.finditer(term, text):
        snippet_start_index = max(match.start() - 30, 0)
        snippet_end_index = min(match.end() + 30, len(text))
        snippet = ('...' if snippet_start_index>0 else '') + text[snippet_start_index: snippet_end_index] + ('...' if snippet_end_index < len(text)-1 else '')
        out_snippets.append(snippet)
        if len(out_snippets) >= limit:
            return out_snippets

    return out_snippets