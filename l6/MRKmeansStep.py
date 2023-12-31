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
        it1 = 0
        it2 = 0
        sumFreqInters = 0

        while it1 < len(doc) and it2 < len(prot):
            if doc[it1] < prot[it2][0]:
                it1 += 1
            elif doc[it1] > prot[it2][0]:
                it2 += 1
            else:
                sumFreqInters += prot[it2][1]
                it1 += 1
                it2 +=1
            
        # as freq of doc terms is 1, their square is 1 too, so their suquare norm sum = len(doc)
        squareNormUnion = len(doc)
        for _, p in prot:
            squareNormUnion += p**2

        return sumFreqInters / float(squareNormUnion - sumFreqInters)


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

        # Each line is a string docid:wor1 word2 ... wordn
        docid, words = line.split(':')
        lwords = words.strip().split()

        best_prototype = None
        highest_similarity = -1

        # Compute Jaccard similarity for each prototype
        for prototype_id, prototype in self.prototypes.items():
            similarity = self.jaccard(prototype, lwords)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_prototype = prototype_id

        # Emit the best prototype with highest similarity and the words
        yield best_prototype, (docid, lwords)


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

        total_docs = 0
        doc_list = []
        word_freq = {}
        
        # Count the frequency of each word and the total number of documents
        for doc_id, words in values:
            total_docs += 1
            doc_list.append(doc_id)
            for word in words:
                if word in word_freq:
                    word_freq[word] += 1
                else:
                    word_freq[word] = 1
                
        # Calculate the new prototype
        new_prototype = []
        for word, freq in word_freq.items():
            new_prototype.append((word, float(freq) / float(total_docs)))
        
        # Sort by alphabetical order before yielding
        yield key, (sorted(doc_list), sorted(new_prototype, key=lambda x: x[0]))

    
    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
            ]


if __name__ == '__main__':
    MRKmeansStep.run()
