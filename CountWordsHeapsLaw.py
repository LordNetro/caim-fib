"""
.. module:: CountWords

CountWords
*************

:Description: CountWords

    Generates a list with the counts and the words in the 'text' field of the documents in an index

:Authors: bejar
    

:Version: 

:Created on: 04/07/2017 11:58 

"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError


import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import string
import argparse

__author__ = 'bejar'


def HeapsLaw(x, k, b):
    return k*(x**b)


def plot(totalWordsNoveli, difWordsNoveli):

    # dibuixem els nostres resultats
    plt.plot(totalWordsNoveli, difWordsNoveli, "b", label="Our results")

    # dibuixem seguint la funcio de Heap trobant els valors optims de k i beta
    popt, pcov = curve_fit(HeapsLaw, totalWordsNoveli, difWordsNoveli)
    plt.plot(totalWordsNoveli, HeapsLaw(totalWordsNoveli, *popt), "r--", label="Heap's Law")

    plt.xlabel("Number of total words")
    plt.ylabel("Number of different words")
    plt.legend()
    plt.title(f'k={popt[0]}, beta={popt[1]}')

    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=False, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    try:

        client = Elasticsearch(timeout=1000)

        difWordsNoveli = []
        totalWordsNoveli = []
        setAllowedWords = set(string.ascii_lowercase + string.ascii_uppercase)

        for i in range(0, 12):

            voc = {}
            sc = scan(client, index="nov" + str(i), query={"query" : {"match_all": {}}})
            for s in sc:
                try:
                    tv = client.termvectors(index="nov" + str(i), id=s['_id'], fields=['text'])
                    if 'text' in tv['term_vectors']:
                        for t in tv['term_vectors']['text']['terms']:
                            if t in voc:
                                voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                            else:
                                voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
                except TransportError:
                    pass
            lpal = []

            for v in voc:
                lpal.append((v.encode("utf-8", "ignore"), voc[v]))

            totalwordCount = 0
            difWordCount = 0

            for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
                # evalua si es una palabra con todas las letras pertenecientes al set de letras permitidas de y solo entonces la cuenta
                if not any(chr(letter) not in setAllowedWords for letter in pal):
                    totalwordCount += cnt
                    difWordCount += 1
            totalWordsNoveli.append(totalwordCount)
            difWordsNoveli.append(difWordCount)

        plot(totalWordsNoveli, difWordsNoveli)

    except NotFoundError:
        print(f'Index does not exist')
