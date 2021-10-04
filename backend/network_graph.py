import itertools

def build_terms_graph(terms_counts, connections_counts):
    out_nodes = []
    out_edges = []
    term_to_id = {}

    for i, (term, counts) in enumerate(terms_counts.items()):
        term_count = len(counts)
        term_to_id[term] = i
        out_nodes.append({'id': i, 'label': term, 'size': term_count})

    for i, (key, counts) in enumerate(connections_counts.items()):
        term1 = key[0]
        term2 = key[1]
        count = len(counts)
        # if count >= 0:
        term1_id = term_to_id[term1]
        term2_id = term_to_id[term2]
        out_edges.append({'id': i, 'from': term1_id, 'to': term2_id, 'width': count})

    return out_nodes, out_edges


def create_network(termCounter, terms_to_include_set, add_n_connections=3, min_connection_threshold=10):
    terms = {}
    connections = {}

    for term in terms_to_include_set:
        terms[term] = termCounter.counts[term]
        connected_terms = termCounter.get_connected_terms(term)
        top_connected_terms =[conn_term for conn_term in sorted(connected_terms, key=lambda t:len(termCounter.get_connection_counts(term,t)), reverse=True)
                              if conn_term not in terms_to_include_set][:add_n_connections]
        for conn_term in top_connected_terms:
            terms[conn_term] = termCounter.counts[conn_term]
            connections[(max(term, conn_term), min(term, conn_term))] = termCounter.get_connection_counts(term,conn_term)

    for t1, t2 in itertools.combinations(terms.keys(), 2):
        connection_counts = termCounter.get_connection_counts(t1,t2)
        if len(connection_counts) > 0 and len(connection_counts) >= min_connection_threshold:
            connections[(max(t1, t2), min(t1, t2))] = connection_counts

    print('Nodes: {0}'.format(len(terms.items())))
    print('Edges: {0}'.format(len(connections.items())))
    nodes, edges = build_terms_graph(terms, connections)
    return nodes, edges