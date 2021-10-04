from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

class KeywordsExtractor():
    def __init__(self):
        self.vectorizer = None
        self.feature_names = None

    def create_model(self):
        self.vectorizer = TfidfVectorizer(max_df=0.35, ngram_range=(1, 1), use_idf=True)

    def load_model(self, model_path):
        with open(model_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
            self.feature_names = self.vectorizer.get_feature_names()

    def fit_model(self, documents):
        self.vectorizer.fit(documents)
        self.feature_names = self.vectorizer.get_feature_names()

    def extract(self, text, n=20):
        result = self.vectorizer.transform([text])
        dense_list = result.todense().tolist()[0]
        keywords = [(self.feature_names[index], round(score, 3)) for index, score in enumerate(dense_list) if score > 0]
        keywords_sorted = sorted(keywords, key=lambda item: item[1], reverse=True)
        keywords_top_n = keywords_sorted[:min(len(keywords_sorted), n)]
        return keywords_top_n

    def save_model(self, model_path):
        with open(model_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)

    def get_idf(self, word, default= 0):
        index = self.vectorizer.vocabulary_.get(word, None)
        if not index:
            return default
        return self.vectorizer.idf_[index]