from collections import defaultdict
import ast
import dateutil.parser
import datetime

class TermCounter():
    def __init__(self):
        self._term_counts = None
        self._term_connections = None
        self._article_id_to_timestamp = None

    def load_terms(self, articles):
        self._term_counts = defaultdict(lambda: set())
        self._term_connections = defaultdict(lambda: set())
        self._article_id_to_timestamp = defaultdict(lambda: set())

        for article in articles:
            terms = ast.literal_eval(article['terms'])
            self._article_id_to_timestamp[article['id']] = article['timestamp']

            for i,t in enumerate(terms):
                self._term_counts[t].add(article['id'])
                other_terms = terms[:i] + terms[i+1:]
                self._term_connections[t].update(other_terms)

    def create_terms_counts_mask(self, range_from=None, range_to=None, min_count=1):
        if range_from is None and range_to is None and min_count ==1:
            return self._term_counts

        if range_from is None:
            range_from = datetime.datetime.min
        if range_to is None:
            range_to = datetime.datetime.max

        out_dict = {}
        for key, value in self._term_counts.items():
            ids_in_range = set(filter(lambda id: range_from <= self._article_id_to_timestamp[id] <= range_to, value))
            if len(ids_in_range) >= min_count:
                out_dict[key] = ids_in_range
        return out_dict

    def get_connection_counts(self, termA, termB):
        ids_A = self._term_counts[termA]
        ids_B = self._term_counts[termB]

        return ids_A.intersection(ids_B)

    def get_connected_terms(self, term):
        return self._term_connections[term]

    def get_counts(self):
        return self._term_counts

    counts = property(get_counts)
    article_id_to_timestamp = property(lambda self:self._article_id_to_timestamp)
