from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError

class ElasticFunctionals:
    def __init__(self, client):
        """
        Constructor para inicializar la clase con un cliente de Elasticsearch.

        :param client: Instancia del cliente de Elasticsearch
        """
        self.client = client

    def count_words(self, index, alpha=False):
        """
        Function to count the words in the 'text' field of an Elasticsearch index.
        
        :param index: Name of the index
        :param alpha: Sort alphabetically if True, else by frequency
        """
        count = 0
        try:
            voc = {}
            sc = scan(self.client, index=index, query={"query": {"match_all": {}}})
            
            for s in sc:
                try:
                    tv = self.client.termvectors(index=index, id=s['_id'], fields=['text'])
                    if 'text' in tv['term_vectors']:
                        for t in tv['term_vectors']['text']['terms']:
                            if t in voc:
                                voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                            else:
                                voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
                except TransportError:
                    pass
            
            lpal = [(v, voc[v]) for v in voc]

            ## Sort alphabetically or by frequency
            #for pal, cnt in sorted(lpal, key=lambda x: x[0 if alpha else 1]):
            #    print(f'{cnt}, {pal}')
            #
            #print('--------------------')
            #print(f'{len(lpal)} Words')
            count = len(lpal)

        except NotFoundError:
            print(f'Index {index} does not exist')

        return count
    
    def count_word_frequency(self, index, alpha=False):
        """
        Function to count the words in the 'text' field of an Elasticsearch index.
        
        :param index: Name of the index
        :param alpha: Sort alphabetically if True, else by frequency
        :return: List of tuples containing (word, count)
        """
        try:
            voc = {}
            sc = scan(self.client, index=index, query={"query": {"match_all": {}}})
            
            for s in sc:
                try:
                    tv = self.client.termvectors(index=index, id=s['_id'], fields=['text'])
                    if 'text' in tv['term_vectors']:
                        for t in tv['term_vectors']['text']['terms']:
                            if t in voc:
                                voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                            else:
                                voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
                except TransportError:
                    pass
            
            # Convert the vocabulary to a sorted list of tuples (word, count)
            sorted_words = sorted(voc.items(), key=lambda x: x[1], reverse=True)
            return sorted_words  # Devuelve la lista de palabras y sus frecuencias
        
        except NotFoundError:
            print(f'Index {index} does not exist')
            return []

