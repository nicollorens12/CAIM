from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from elasticsearch.client import CatClient
from elasticsearch.exceptions import NotFoundError
import argparse
import numpy as np
import operator

def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

def search(s,query, nhits):
    q = Q('query_string',query=query[0])
    for i in range(1, len(query)):
        q &= Q('query_string',query=query[i])
    s = s.query(q)
    response = s[0:nhits].execute()
    return response

def document_term_vector(client, index, doc_id):
    termvector = client.termvectors(index=index, id=doc_id, fields=['text'],
                                            positions=False, term_statistics=True)
    file_td = {}
    file_df = {}
    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())

def toTFIDF(client, index, doc_id):
    file_tv, file_df = document_term_vector(client, index, doc_id)
    max_freq = max([f for _, f in file_tv])
    dcount = doc_count(client, index)
    tfidfw = {}
    for (t, w),(_, df) in zip(file_tv, file_df):
        tf = w / max_freq
        idf = np.log2(dcount / df)
        tfidfw[t] = ((tf * idf))
    
    return normalize(tfidfw)

def normalize(tw):
    norm = np.sqrt(sum([w * w for w in tw.values()]))
    return {t: w / norm for t, w in tw.items()}


def rocchio_update(query_vector, doc_vectors, alpha, beta, k,r):
    old_query = {term: query_vector.get(term,0)*alpha for term in set(query_vector)}
    doc_vectors = {term: doc_vectors.get(term,0)*beta/k for term in set(doc_vectors)}
    new_query = {}
    new_query = {term: doc_vectors.get(term, 0) + old_query.get(term, 0) for term in set(doc_vectors) | set(old_query)}
    new_query = sorted(new_query.items(), key=operator.itemgetter(1), reverse = True) 
    new_query = new_query[:r]
    return dict((term, val) for (term, val) in new_query) 

def queryToDict(query):
    query_dict = {}
    for elem in query:
        if '^' in elem:
            key, value = elem.split('^')
            value = float(value)
        else:
            key = elem
            value = 1.0
        query_dict[key] = value
        
    return normalize(query_dict)

def dictToquery(di):
    query = []
    for elem in di:
        q = elem + '^' + str(di[elem])
        query.append(q)
    return query

def query_to_string(query_vector):
    return ' '.join([f"{term}^{weight}" for term, weight in query_vector.items()])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', required=True, help='Index to search')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')
    parser.add_argument('--alpha', default=1.0, type=float, help='Alpha parameter for Rocchio algorithm')
    parser.add_argument('--beta', default=0.1, type=float, help='Beta parameter for Rocchio algorithm')
    parser.add_argument('--nrounds', default=10, type=int, help='Number of Rocchio iterations')
    parser.add_argument('--k', default=10, type=int, help='Number of top documents to consider for Rocchio update')
    parser.add_argument('--r', default=2, type=int, help='Number of terms to retain in the updated query')
    args = parser.parse_args()

    index = args.index
    query = args.query
    alpha = args.alpha
    beta = args.beta
    nrounds = args.nrounds
    k = args.k
    r = args.r
    try:
        client = Elasticsearch( hosts=['http://localhost:9200'], request_timeout=1000)
        s = Search(using=client, index=index)
        print("Initial Query")
        response = search(s, query, k)
        print (f"{response.hits.total['value']} Documents")
        if query is not None:
            for _ in range(nrounds):
                print('-----------------------------------------------------------------')
                query_vector = queryToDict(query)
                doc_vectors = {}
                for res in response:
                    file_tw = toTFIDF(client, index, res.meta.id)
                    doc_vectors = {t: doc_vectors.get(t,0) + file_tw.get(t,0) for t in set(file_tw) | set(doc_vectors)}   
                
                print(f'Query: {query_to_string(query_vector)}')
                dictQuuery = rocchio_update(query_vector, doc_vectors, alpha, beta, k, r)
                print(f'Updated Query: {query_to_string(dictQuuery)}')
                query = dictToquery(dictQuuery)
                response = search(s, query, k)
                print (f"{response.hits.total['value']} Documents")
                
            for hit in response:
                print(f'ID= {hit.meta.id} SCORE={hit.meta.score}')
                print(f'PATH= {hit.path}')
                print(f'TEXT: {hit.text[:50]}')
                print('-----------------------------------------------------------------')
        else:
            print('No query parameters passed')
        
        print(f'Total Documents: {response.hits.total["value"]}')
    except NotFoundError:
        print(f'Index {index} does not exists')
    except Exception as e:
        print(f"Error in elastic search connection {e}")

