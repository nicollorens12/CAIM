"""
.. module:: MRKmeansDef

MRKmeansDef
*************

:Description: MRKmeansDef

    

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 7:42 

"""

from mrjob.job import MRJob
from mrjob.step import MRStep

__author__ = 'bejar'


class MRKmeansStep(MRJob):
    prototypes = {}

    def jaccard(self, prot, doc):
        """
        Compute here the Jaccard similarity between  a prototype and a document
        prot should be a list of pairs (word, probability)
        doc should be a list of words
        Words must be alphabeticaly ordered

        The result should be always a value in the range [0,1]
        """
        prot_words = set(word for word, _ in prot)
        doc_words = set(doc)
        intersection = len(prot_words & doc_words)
        union = len(prot_words | doc_words)
        return intersection / union if union > 0 else 0

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files

        :return:
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    def load_data(self):
        """
        Loads the current cluster prototypes

        :return:
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """

        doc_id, words = line.split(':')
        doc_words = sorted(words.split())
        best_cluster = None
        max_similarity = -1

        for cluster, prot in self.prototypes.items():
            similarity = self.jaccard(prot, doc_words)
            if similarity > max_similarity:
                max_similarity = similarity
                best_cluster = cluster

        # Emit the best cluster and document words
        yield best_cluster, doc_words

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """

        word_count = {}
        num_docs = 0

        for doc_words in values:
            num_docs += 1
            for word in doc_words:
                word_count[word] = word_count.get(word, 0) + 1

        # Calculate the new prototype as word frequencies
        new_prototype = sorted((word, count / num_docs) for word, count in word_count.items())
        yield key, new_prototype

    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
            ]


if __name__ == '__main__':
    MRKmeansStep.run()