from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import argparse
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
import operator



def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])



def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())



def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get the frequency of the term in the document, and the number of documents
    # that contain the term
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = []
    for (t, w),(_, df) in zip(file_tv, file_df):
        tf  = w / max_freq
        idf = np.log2((dcount / df))
        tfidfw.append((t, tf * idf))

    return normalize(tfidfw)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nhits', default=10, type=int, help='Number of hits to return')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    index = args.index
    query = args.query
    print(query)
    nhits = args.nhits

    nRounds = 5
    ALPHA = 0.95
    BETA = 0.05
    R = 3

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        if query is not None:
            for i in range(0, nRounds):
                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=query[i])

                s = s.query(q)
                response = s[0:nhits].execute()

                queries = {}

                for word in query:
                    if ('^' in word):
                        term, value = word.split('^')
                        queries[term] = float(value)
                    else:
                        queries = 1.0

                docWeights = {}

                for r in response:
                    tfIdfDoc = toTFIDF(client, index, r.meta.id)
                    for t in set(tfIdfDoc) | set(docWeights):
                        docWeights[t] = docWeights.get(t,0) + tfIdfDoc.get(t,0)

                # beta*(d_1 + d_2 + ... + dk)/k
                for t in set(docWeights):
                    docWeights[t] = BETA*docWeights.get(t,0)/nhits

                # alpha * lastQuery
                lastQuery = {}
                for t in set(queries):
                    lastQuery[t] = ALPHA*queries.get(t,0)

                # newquery = docWeights + lastQuery
                newQuery = {}
                for t in set(lastQuery) | set(docWeights):
                    newQuery[t] = docWeights.get(t,0) + lastQuery.get(t,0)

                newQuery = sorted(newQuery.items(), key=operator.itemgetter(1), reverse=True)[:R]

                query = []
                for (term, value) in newQuery:
                    query.append(term + '^' + str(value))



            for r in response:  # only returns a specific number of results
                print(f'ID= {r.meta.id} SCORE={r.meta.score}')
                print(f'PATH= {r.path}')
                print(f'TEXT: {r.text[:50]}')
                print('-----------------------------------------------------------------')

        else:
            print('No query parameters passed')

        print (f"{response.hits.total['value']} Documents")

    except NotFoundError:
        print(f'Index {index} does not exists')

