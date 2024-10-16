from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Index, analyzer, tokenizer
import os
import codecs

class IndexFiles:
    def __init__(self, client, index, token='standard', filters=['lowercase']):
        """
        Constructor para inicializar la clase con un cliente de Elasticsearch, el índice, el tokenizador y los filtros.

        :param client: Instancia del cliente de Elasticsearch
        :param index: Nombre del índice donde se almacenarán los archivos
        :param token: Tokenizador para el análisis del texto (default: 'standard')
        :param filters: Filtros para el análisis del texto (default: ['lowercase'])
        """
        self.client = client
        self.index = index
        self.token = token
        self.filters = filters
        self.my_analyzer = analyzer(
            'default',
            type='custom',
            tokenizer=tokenizer(self.token),
            filter=self.filters
        )

    def generate_files_list(self, path):
        """
        Genera una lista de todos los archivos dentro de un directorio.

        :param path: Ruta del directorio
        :return: Lista de rutas de archivos
        """
        if path[-1] == '/':
            path = path[:-1]

        lfiles = []
        for root, _, files in os.walk(path):
            for f in files:
                lfiles.append(os.path.join(root, f))
        return lfiles

    def index_files(self, path):
        """
        Indexa todos los archivos dentro de un directorio especificado.

        :param path: Ruta del directorio
        """
        lfiles = self.generate_files_list(path)
        print(f'Indexando {len(lfiles)} archivos')
        print('Leyendo archivos...')

        ldocs = []
        for f in lfiles:
            with codecs.open(f, "r", encoding='iso-8859-1') as ftxt:
                text = ftxt.read()
            ldocs.append({'_op_type': 'index', '_index': self.index, 'path': f, 'text': text})

        # Elimina el índice si ya existe y luego crea uno nuevo
        try:
            ind = Index(self.index, using=self.client)
            ind.delete()
        except NotFoundError:
            pass

        ind.settings(number_of_shards=1)
        ind.create()
        ind = Index(self.index, using=self.client)

        # Configura el analizador por defecto
        ind.close()  # el índice debe estar cerrado para configurar el analizador
        ind.analyzer(self.my_analyzer)

        # Configura el campo "path" para que no sea tokenizado (coincidencia exacta)
        self.client.indices.put_mapping(index=self.index, body={
            "properties": {
                "path": {
                    "type": "keyword",
                }
            }
        })

        ind.save()
        ind.open()
        print("Configuraciones del índice:", ind.get_settings())

        # Ejecuta las operaciones de indexación de forma masiva
        print('Indexando documentos...')
        bulk(self.client, ldocs)

    def get_indexed_paths(self):
        """
        Recupera los paths de todos los documentos indexados.

        :return: Lista de paths de documentos indexados
        """
        s = self.client.search(index=self.index, body={
            "_source": ["path"],
            "query": {
                "match_all": {}
            }
        })

        return [hit["_source"]["path"] for hit in s['hits']['hits']]
