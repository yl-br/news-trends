import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)
sys.path.insert(0,parentdir)

from flask import Flask
from flask import jsonify
import network_graph
import trending_terms
import datetime
from postgres_adapter import PostgresAdapter
from term_counter import TermCounter
import headlines_creator
import utilities


def initialize_data():
    print("Backend App initializing")

    global termCounter, articles, top_terms, headlines, headlines_terms, trends, trends_terms, terms_for_network

    postgresAdapter = PostgresAdapter(db_url=os.getenv('DATABASE_URL', None))
    postgresAdapter.connect()
    articles = postgresAdapter.get_all_features_in_range(datetime.datetime.utcnow() - datetime.timedelta(days=8), datetime.datetime.utcnow())
    postgresAdapter.close()

    print("Articles= {0}".format(len(articles)))

    termCounter = TermCounter()
    termCounter.load_terms(articles)

    print("Terms= {0}".format(len(termCounter.counts.keys())))

    top_terms = sorted(termCounter.counts.keys(), key=lambda key: len(termCounter.counts[key]), reverse=True)
    headlines, headlines_terms = headlines_creator.create_headlines(articles)
    trends, trends_terms = trending_terms.get_trends(termCounter)

    terms_for_network = trends_terms | headlines_terms | set(top_terms[:100])
    print("Backend App initialization finished.")


# ------------------------------------------------------------------------------
print("Backend App started..")
app = Flask(__name__, static_folder='public', static_url_path='/public')
app.config['JSON_AS_ASCII'] = False

initialize_data()
# ------------------------------------------------------------------------------

@app.route('/refresh-data', methods=['GET'])
def refresh_data():
    initialize_data()
    return jsonify({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/")
def get_index():
    return app.send_static_file('index.html')

@app.route('/terms', methods=['GET'])
def get_terms():
    return jsonify(list(terms_for_network))

@app.route('/trends', methods=['GET'])
def get_trends():
    weekly_terms = [(term, len(termCounter.counts[term])) for term in top_terms[:10]]
    return jsonify({'days':trends,'week':weekly_terms})

@app.route('/network', methods=['GET'])
def get_network():
    nodes, edges = network_graph.create_network(termCounter, terms_for_network, add_n_connections=2, min_connection_threshold=12)
    return jsonify({'nodes':nodes,'edges':edges})


@app.route('/headlines', methods=['GET'])
def get_headlines():
    return jsonify(headlines)

@app.route('/terms/<term>', methods=['GET'])
def get_term_citations(term):
    term_articles = termCounter.counts[term]
    out_citations = []

    for article_id in term_articles:
        article_index = list(map(lambda a:a['id'],articles)).index(article_id)
        article = articles[article_index]
        all_text = ' ' + (article['title'] or '') +' ' + (article['description'] or '') + ' ' + (article['body'] or '') + ' '
        all_text = utilities.clean_text(all_text)
        snippets = utilities.find_snippets(all_text, term, limit=2)
        out_citations.append({'id':article_id, 'timestamp':article['timestamp'], 'source':article['source'], 'url':article['url'],
                                'title':utilities.clean_text(article['title']),'snippets':snippets})

    return jsonify(out_citations)



@app.route('/connections/<termA>/<termB>', methods=['GET'])
def get_connection(termA, termB):
    counts = termCounter.get_connection_counts(termA, termB)

    out_occurrences = []

    for article_id in counts:
        article_index = list(map(lambda a:a['id'],articles)).index(article_id)
        article = articles[article_index]
        all_text = ' ' + (article['title'] or '') +' ' + (article['description'] or '') + ' ' + (article['body'] or '') + ' '
        all_text = utilities.clean_text(all_text)

        snippetA = utilities.find_snippets(all_text, termA, limit=1)
        snippetB = utilities.find_snippets(all_text, termB, limit=1)

        out_occurrences.append({'id':article_id, 'timestamp': article['timestamp'],'source':article['source'],'url':article['url'],
                                'title':utilities.clean_text(article['title']),'snippets':snippetA+snippetB})

    return jsonify(out_occurrences)


@app.route('/connections/<term>', methods=['GET'])
def get_term_connections(term, top_n=15):
    conn_terms = termCounter.get_connected_terms(term)
    conn_term_and_counts = []
    for conn_term in conn_terms:
        counts = termCounter.get_connection_counts(term, conn_term)
        conn_term_and_counts.append((conn_term,  counts, len(counts)))

    conn_term_and_counts.sort(key=lambda tup:tup[2], reverse=True)
    out_connections = {tup[0]: list(tup[1]) for tup in conn_term_and_counts[:top_n]}
    return jsonify(out_connections)


@app.route('/terms/popularity/<term>', methods=['GET'])
def get_term_popularity(term):
    term_occurrences = termCounter.counts[term] # (timestamp, article_id)

    out_occurrences = []

    for article_id in term_occurrences:
        article_index = list(map(lambda a:a['id'], articles)).index(article_id)
        article = articles[article_index]
        out_occurrences.append({'article_id':article_id,'title':utilities.clean_text(article['title']),'timestamp':article['timestamp'],'source':article['source']})

    return jsonify(out_occurrences)

@app.route('/dataset-info', methods=['GET'])
def get_dataset_info():
    dataset_info = [{'id': a['id'], 'timestamp':a['timestamp'], 'source':a['source']} for a in articles]
    return jsonify(dataset_info)




if __name__ == '__main__':
    app.run(debug=False)