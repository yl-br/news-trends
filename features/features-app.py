import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)
sys.path.insert(0,parentdir)

import logging
import argparse
import traceback
import ast
from postgres_adapter import PostgresAdapter
from features.keywords_extractor import KeywordsExtractor
from features.tokenizer import tokenize
from features.terms_matcher import TermsMatcher


def main():
    logging.info("\n"*5 + "started...")

    postgresAdapter = PostgresAdapter(db_url=os.getenv('DATABASE_URL', args.db_url))
    postgresAdapter.connect()

    if args.reset:
        postgresAdapter.drop_features_table()

    postgresAdapter.create_features_table_if_not_exist()
    postgresAdapter.copy_crawler_table_to_features_table()
    postgresAdapter.delete_duplicates_in_features()


    # Tokenizing.

    articles = postgresAdapter.get_all_features()
    logging.info("Number of articles in db: {0}".format(len(articles)))

    if args.rewrite:
        articles_to_tokenize = articles
    else:
        articles_to_tokenize = list(filter(lambda a: a['title_tokens'] is None, articles))

    logging.info("Number of articles to tokenize: {0}".format(len(articles_to_tokenize)))

    with open('features/hebrew_stop_words.txt', encoding="utf8") as file:
        hebrew_stop_words = file.read().split('\n')

    for i, article in enumerate(articles_to_tokenize):
        title_tokens = tokenize(article['title'], hebrew_stop_words)
        description_tokens = tokenize(article['description'], hebrew_stop_words)
        body_tokens = tokenize(article['body'], hebrew_stop_words)
        postgresAdapter.update_features_tokens(article['id'], title_tokens, description_tokens, body_tokens)
        logging.debug("Tokenizing -> {0} / {1} .".format(i + 1, len(articles_to_tokenize)))

    logging.info("Finished tokenizing.")


    # Keywords extraction.

    get_all_article_tokens = lambda article: ' ' + article['title_tokens'] + ' ' + article['description_tokens'] + ' ' + article['body_tokens'] + ' '

    articles = postgresAdapter.get_all_features()
    if args.rewrite:
        articles_to_extract_keywords = articles
    else:
        articles_to_extract_keywords = list(filter(lambda a: a['keywords'] is None, articles))

    logging.info("Number of articles to extract keywords: {0}".format(len(articles_to_extract_keywords)))


    logging.info("Creating tf-idf model..")
    keywordsExtractor = KeywordsExtractor()
    keywordsExtractor.create_model()
    corpus = [get_all_article_tokens(article) for article in articles]
    logging.info("Fitting tf-idf model. Corpus size={0}.".format(len(corpus)))
    keywordsExtractor.fit_model(corpus)
    logging.info("Tf-idf model ready.")


    for i, article in enumerate(articles_to_extract_keywords):
        text = get_all_article_tokens(article)

        keywords = keywordsExtractor.extract(text, n=20)
        postgresAdapter.update_features_keywords(article['id'], keywords)
        logging.debug("Extracting keywords -> {0} / {1} .".format(i + 1, len(articles_to_extract_keywords)))

    logging.info("Finished keywords extraction.")


    # Terms matching.
    articles = postgresAdapter.get_all_features()
    if args.rewrite:
        articles_to_match_terms = articles
    else:
        articles_to_match_terms = list(filter(lambda a: a['terms'] is None, articles))

    logging.info("Number of articles to match terms: {0}".format(len(articles_to_match_terms)))

    termMatcher = TermsMatcher()
    termMatcher.load_terms("features/hebrew-wikipedia-terms-extraction/output/hebrew_wikipedia_titles.txt")

    for i,article in enumerate(articles_to_match_terms):
        text = get_all_article_tokens(article)
        keywords = ast.literal_eval(article['keywords'])
        terms_found = termMatcher.match_terms(text, keywords)
        postgresAdapter.update_features_terms(article['id'], terms_found)
        logging.debug("Matching terms -> {0} / {1} .".format(i+1, len(articles_to_match_terms)))


    logging.info("Finished matching terms.")

    postgresAdapter.close()
    logging.info("Finished.")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--log_level", type=str, default="INFO")
        parser.add_argument("--db_url", type=str, default=None)
        parser.add_argument('--reset', dest='reset', action='store_true', default=False)
        parser.add_argument('--rewrite', dest='rewrite', action='store_true', default=False)
        args = parser.parse_args()

        handlers = [logging.FileHandler(filename='features/features.log'), logging.StreamHandler(sys.stdout)]
        logging.basicConfig(handlers=handlers, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=args.log_level)

        main()
    except Exception as e:
        logging.error("Major error occurred.\n" + traceback.format_exc())
    finally:
        sys.exit()