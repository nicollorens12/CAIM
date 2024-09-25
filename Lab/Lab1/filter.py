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
import argparse
import csv
import re

__author__ = 'bejar'

def is_valid_word(word):
    """Check if the word contains only alphabetic characters."""
    return re.match("^[A-Za-z]+$", word) is not None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    parser.add_argument('--output', default='output.csv', help='Output CSV file name')
    args = parser.parse_args()

    index = args.index

    try:
        client = Elasticsearch(hosts=['http://localhost:9200'], request_timeout=1000)
        voc = {}
        sc = scan(client, index=index, query={"query": {"match_all": {}}})
        
        for s in sc:
            try:
                tv = client.termvectors(index=index, id=s['_id'], fields=['text'])
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
            if is_valid_word(v):  # Check if the word is valid
                lpal.append((v.encode("utf-8", "ignore"), voc[v]))

        # Sort and prepare data for CSV output
        if args.alpha:
            lpal.sort(key=lambda x: x[0].decode("utf-8"))  # Ordena lexicográficamente por la palabra
        else:
            lpal.sort(key=lambda x: x[1])  # Ordena por el conteo

        # Write results to CSV
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Count', 'Word'])  # Write header
            for pal, cnt in lpal:
                csvwriter.writerow([cnt, pal.decode("utf-8")])  # Write each word and its count

        print('Results saved to', args.output)
        print('--------------------')
        print(f'{len(lpal)} Words')
    
    except NotFoundError:
        print(f'Index {index} does not exist')
