from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from collections import Counter
import pandas as pd
from itertools import chain
import ast
import utilities

def create_headlines(articles):
    articles_text = [a['title_tokens'] + ' ' + a['description_tokens'] for a in articles]

    vec = TfidfVectorizer(max_features=10000, max_df=0.4)
    features = vec.fit_transform(articles_text)

    clusters = DBSCAN(eps=0.7, min_samples=5, metric='cosine').fit(features.toarray()).labels_

    cluster_to_indexes = pd.Series(range(len(clusters))).groupby(clusters, sort=False).apply(list).to_dict()
    del cluster_to_indexes[-1]
    cluster_to_indexes = dict(filter(lambda item: len(item[1])>= 3, cluster_to_indexes.items())) # only clusters with minimum number of articles.

    # latest_timestamp_clusters = sorted(cluster_to_indexes.keys(), key=lambda key:max(map(lambda index: articles[index]['timestamp'], cluster_to_indexes[key])), reverse=True)[:3]
    top_count_clusters = sorted(cluster_to_indexes.keys(), key=lambda key: len(cluster_to_indexes[key]), reverse=True)

    selected_clusters = top_count_clusters[:7]

    out_used_terms = set()
    out_headlines = []
    for cluster in selected_clusters:
        cluster_articles = sorted(map(lambda idx: articles[idx],cluster_to_indexes[cluster]), key=lambda a: a['timestamp'], reverse=True)
        titles = [{'title':utilities.clean_text(a['title']),'source':a['source'], 'url':a['url'], 'timestamp':a['timestamp']} for a in cluster_articles]
        common_terms = Counter(chain.from_iterable(ast.literal_eval(a['terms']) for a in cluster_articles)).most_common(5)
        common_terms_list, _ = zip(*common_terms)
        out_headlines.append({'articles': titles, 'common_terms': common_terms_list})
        out_used_terms.update(common_terms_list)

    out_headlines.sort(key=lambda x: max(map(lambda a: a['timestamp'],x['articles'])), reverse=True)
    return out_headlines, out_used_terms

