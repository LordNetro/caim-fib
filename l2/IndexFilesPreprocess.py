"""
.. module:: IndexFilesPreprocess

IndexFiles
******

:Description: IndexFilesPreprocess

    Indexes a set of files under the directory passed as a parameter (--path)
    in the index name passed as a parameter (--index)

    Add configuration of the default analizer: tokenizer  (--token) and filter (--filter)

    --filter must be always the last flag

    If the index exists it is dropped and created new

    Documentation for the analyzer configuration:

    https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html

:Authors:
    bejar

:Version:

:Date:  23/06/2017
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
import argparse
import os
import codecs
from elasticsearch_dsl import Index, analyzer, tokenizer, token_filter

# Define filters
length_filter = token_filter('length_filter', type='length', min=2, max=20)
word_delimiter_filter = token_filter('word_delimiter_filter', type='word_delimiter')
ngram_filter = token_filter('ngram_filter', type='ngram', min_gram=2, max_gram=15)
edge_ngram_filter = token_filter('edge_ngram_filter', type='edge_ngram', min_gram=1, max_gram=15)

def generate_files_list(path):
    """
    Generates a list of all the files inside a path
    :param path:
    :return:
    """
    if path[-1] == '/':
        path = path[:-1]

    lfiles = []

    for lf in os.walk(path):
        if lf[2]:
            for f in lf[2]:
                lfiles.append(lf[0] + '/' + f)
    return lfiles


__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, default=None, help='Path to the files')
    parser.add_argument('--index', required=True, default=None, help='Index for the files')
    parser.add_argument('--token', default='standard', choices=['standard', 'whitespace', 'classic', 'letter', 'uax_url_email', 'thai'],
                        help='Text tokenizer')
    parser.add_argument('--filter', default=['lowercase'], nargs=argparse.REMAINDER, help='Text filter: lowercase, '
                                                                                          'asciifolding, stop, porter_stem, kstem, snowball, english_stop, length_filter, word_delimiter_filter, ngram_filter, edge_ngram_filter')

    args = parser.parse_args()

    path = args.path
    index = args.index

    # check if the filters are valid
    valid_filters = ['lowercase', 'asciifolding', 'stop', 'stemmer', 'porter_stem', 'kstem', 'snowball', 'english_stop',
                     'length_filter', 'word_delimiter_filter', 'ngram_filter', 'edge_ngram_filter']

    for f in args.filter:
        if f not in valid_filters:
            raise NameError(f'Invalid filter. Must be a subset of: {", ".join(valid_filters)}')


    ldocs = []

    # Reads all the documents in a directory tree and generates an index operation for each
    lfiles = generate_files_list(path)
    print('Indexing %d files' % len(lfiles))
    print('Reading files ...')
    for f in lfiles:
        ftxt = codecs.open(f, "r", encoding='iso-8859-1')
        text = ''
        for line in ftxt:
            text += line
        # Insert operation for a document with fields' path' and 'text'
        ldocs.append({'_op_type': 'index', '_index': index, 'path': f, 'text': text})

    client = Elasticsearch(timeout=1000)

    # List of all available filters
    all_filters = {
        'lowercase': 'lowercase',
        'asciifolding': 'asciifolding',
        'stop': 'stop',
        'stemmer': 'stemmer',
        'porter_stem': 'porter_stem',
        'kstem': 'kstem',
        'snowball': 'snowball',
        'english_stop': 'english_stop',
        'length_filter': length_filter,
        'word_delimiter_filter': word_delimiter_filter,
        'ngram_filter': ngram_filter,
        'edge_ngram_filter': edge_ngram_filter
    }

    # Extract the filters based on args.filter
    active_filters = [all_filters[f] for f in args.filter]

    # Tokenizers: whitespace classic standard letter
    my_analyzer = analyzer('default',
                           type='custom',
                           tokenizer=tokenizer(args.token),
                           filter=active_filters
                           )

    try:
        # Drop index if it exists
        ind = Index(index, using=client)
        ind.delete()
    except NotFoundError:
        pass
    # then create it
    ind.settings(number_of_shards=1)
    ind.create()
    ind = Index(index, using=client)

    # configure default analyzer
    ind.close()  # index must be closed for configuring analyzer
    ind.analyzer(my_analyzer)

    # configure the path field so it is not tokenized and we can do exact match search
    client.indices.put_mapping(index=index, body={
        "properties": {
            "path": {
                "type": "keyword",
            }
        }
    })

    ind.save()
    ind.open()
    print("Index settings=", ind.get_settings())
    # Bulk execution of elastic search operations (faster than executing all one by one)
    print('Indexing ...')
    bulk(client, ldocs)
