from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.client import CatClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q

import numpy as np

class TFIDFViewer:
    def __init__(self, client):
        """
        Constructor para inicializar la clase con un cliente de Elasticsearch.

        :param client: Instancia del cliente de Elasticsearch
        """
        self.client = client

    def search_file_by_path(self, index, path):
        """
        Busca un archivo utilizando su ruta.

        :param index: Índice donde se busca.
        :param path: Ruta del archivo a buscar.
        :return: ID del documento encontrado.
        """
        s = Search(using=self.client, index=index)
        q = Q('match', path=path)  # búsqueda exacta en el campo de ruta
        s = s.query(q)
        result = s.execute()

        lfiles = [r for r in result]
        if len(lfiles) == 0:
            raise NameError(f'File [{path}] not found')
        else:
            return lfiles[0].meta.id

    def document_term_vector(self, index, doc_id):
        """
        Retorna el vector de términos de un documento y sus estadísticas, en forma de dos listas
        ordenadas de pares (palabra, cantidad).

        :param index: Índice donde está el documento.
        :param doc_id: ID del documento.
        :return: Listas de frecuencia de términos y frecuencia de documentos.
        """
        termvector = self.client.termvectors(index=index, id=doc_id, fields=['text'],
                                             positions=False, term_statistics=True)

        file_td = {}
        file_df = {}

        if 'text' in termvector['term_vectors']:
            for t in termvector['term_vectors']['text']['terms']:
                file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
                file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
        return sorted(file_td.items()), sorted(file_df.items())

    def to_tfidf(self, index, doc_id):
        """
        Calcula los pesos TF-IDF de un documento.

        :param index: Índice donde está el documento.
        :param doc_id: ID del documento.
        :return: Vector de pesos TF-IDF normalizados.
        """
        # Obtener las frecuencias de los términos en el documento y la cantidad de documentos
        file_tv, file_df = self.document_term_vector(index, doc_id)

        max_freq = max([f for _, f in file_tv])
        dcount = self.doc_count(index)

        tfidfw = []
        for (t, w),(_, df) in zip(file_tv, file_df):
            tf = w / max_freq
            idf = np.log2(dcount / df)
            tfidfw.append((t, tf * idf))

        return self.normalize(tfidfw)

    def normalize(self, tw):
        """
        Normaliza los pesos para que formen un vector unitario.

        :param tw: Vector de términos y pesos.
        :return: Vector de pesos normalizado.
        """
        norm = np.sqrt(sum([w * w for _, w in tw]))
        return [(t, w / norm) for t, w in tw]

    def cosine_similarity(self, tw1, tw2):
        """
        Calcula la similitud coseno entre dos vectores de peso, ordenados alfabéticamente.

        :param tw1: Primer vector de términos y pesos.
        :param tw2: Segundo vector de términos y pesos.
        :return: Similitud coseno entre los dos vectores.
        """
        i = 0
        j = 0
        sim = 0
        while i < len(tw1) and j < len(tw2):
            if tw1[i][0] == tw2[j][0]:
                sim += tw1[i][1] * tw2[j][1]
                i += 1
                j += 1
            elif tw1[i][0] < tw2[j][0]:
                i += 1
            else:
                j += 1
        return sim

    def doc_count(self, index):
        """
        Retorna la cantidad de documentos en un índice.

        :param index: Índice a consultar.
        :return: Cantidad de documentos en el índice.
        """
        return int(CatClient(self.client).count(index=[index], format='json')[0]['count'])

    def compare_files(self, index1, file1_path, index2, file2_path, print_tfidf=False):
        """
        Compara dos archivos calculando la similitud coseno de sus vectores TF-IDF,
        permitiendo que los archivos provengan de diferentes índices.

        :param index1: Índice donde está el primer documento.
        :param index2: Índice donde está el segundo documento.
        :param file1_path: Ruta del primer archivo.
        :param file2_path: Ruta del segundo archivo.
        :param print_tfidf: Si es True, imprime los vectores TF-IDF.
        :return: Similitud coseno entre los dos archivos.
        """
        try:
            # Obtener los IDs de los archivos en sus respectivos índices
            file1_id = self.search_file_by_path(index1, file1_path)
            file2_id = self.search_file_by_path(index2, file2_path)

            # Calcular los vectores TF-IDF para cada archivo en su índice
            file1_tw = self.to_tfidf(index1, file1_id)
            file2_tw = self.to_tfidf(index2, file2_id)

            if print_tfidf:
                print(f'TFIDF FILE {file1_path} from index {index1}')
                self.print_term_weight_vector(file1_tw)
                print('---------------------')
                print(f'TFIDF FILE {file2_path} from index {index2}')
                self.print_term_weight_vector(file2_tw)
                print('---------------------')

            # Calcular y retornar la similitud coseno entre ambos vectores TF-IDF
            similarity = self.cosine_similarity(file1_tw, file2_tw)
            return similarity

        except NotFoundError as e:
            print(f'Index {index1} or {index2} does not exist: {str(e)}')


    def print_term_weight_vector(self, twv):
        """
        Imprime el vector de términos y sus correspondientes pesos.

        :param twv: Vector de términos y pesos.
        :return: None
        """
        for t, w in twv:
            print(f'{t} -> {w}')
