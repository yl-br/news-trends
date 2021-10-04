import re

class TermsMatcher():
    def __init__(self):
        self.wiki_ngram_titles_set = set()
        self.wiki_unigram_titles_set = set()

    def load_terms(self, wikipedia_titles_txt_file):
        with open(wikipedia_titles_txt_file, encoding='utf-8', newline='') as file:
            for line in file:
                if ' ' in line:
                    self.wiki_ngram_titles_set.add(line.strip())
                else:
                    self.wiki_unigram_titles_set.add(line.strip())

    def match_terms(self, text, keywords):
        titles_in_article = [title for title in self.wiki_ngram_titles_set if ' ' + title + ' ' in text]

        keywords_list = [k[0] for k in keywords]
        keywords_matched_titles = set(keywords_list).intersection(self.wiki_unigram_titles_set)

        extracted_bigrams = self.extract_bigrams(text, keywords_list[:15])

        terms = list(set(titles_in_article + list(keywords_matched_titles) + extracted_bigrams))
        return terms

    def extract_bigrams(self, text, keywords_list, count_threshold=3):
        out_bigrams = []

        for keyword in keywords_list:
            for i, match in enumerate(re.finditer(keyword, text)):
                start = text.rfind(' ', 0, match.start()) + 1
                end = text.find(' ', match.end())

                head_end = text.find(' ', end+1)
                if head_end >= 0:
                    head_bigram = text[start: head_end]
                else:
                    head_bigram = ''

                tail_start = text.rfind(' ', 0, start - 1)
                if tail_start >= 0:
                    tail_bigram = text[tail_start + 1: end]
                else:
                    tail_bigram = ''

                if head_bigram != '' and text.count(head_bigram) >= count_threshold:
                    out_bigrams.append(head_bigram)
                if tail_bigram != '' and text.count(tail_bigram) >= count_threshold:
                    out_bigrams.append(tail_bigram)

        return out_bigrams
