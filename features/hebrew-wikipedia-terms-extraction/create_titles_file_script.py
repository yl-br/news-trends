import pandas as pd
import re
import string

def clean_title(title):
    if title is None or type(title) != str:
        print("Unmatching value for tokenizing: {0}".format(title))
        return ''

    title = re.sub("([\(\[]).*?([\)\]])", "", title) # remove brackets and its content.

    title = title.replace('_', ' ')
    title = title.replace('-', ' ')
    title = title.replace('–', ' ')

    title = title.translate(str.maketrans('', '', string.punctuation + string.digits))

    # re.match("^[0-9 ]+$", title): # Only spaces and digits.
    if not re.match(r"[א-ת]+", title): # title doesn't contain hebrew characters.
        return ''
    if len(title) < 4:
        return ''
    if title in hebrew_stop_words:
        return ''

    return title.strip()


pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199


df_all = pd.read_csv('hewiki-20210301-all-titles', delimiter="\t")

with open('../hebrew_stop_words.txt', encoding="utf8") as file:
    hebrew_stop_words = file.read().split('\n')

print(df_all.head())
print(df_all.shape)
print(df_all[df_all.page_namespace == 0].shape)

df = df_all[df_all.page_namespace == 0]

df = df.assign(clean_title=df['page_title'].map(clean_title))

df = df[df['clean_title'] != '']


print(df.shape)

print(df.sample(5))

df.to_csv("output/hebrew_wikipedia_titles_comparison.csv", doublequote=False, encoding='utf-8',
          escapechar="\t", index=False, columns=['page_title','clean_title'])

titles = df['clean_title'].unique()

print(len(titles))


pd.DataFrame(titles).to_csv("output/hebrew_wikipedia_titles.txt", doublequote=False, encoding='utf-8',
                            escapechar="\t", index=False, header=False)