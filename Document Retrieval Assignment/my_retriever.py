"""
The retriever of Document Retrieval System
"""

from collections import Counter
from operator import itemgetter
import math


class Retrieve:
    """
    The class for Retriever
    """

    def __init__(self, index, term_weighting):
        """
        Create new Retrieve object storing index and term weighting scheme

        :param index: The index dictionary
        :param term_weighting: The term weighting scheme, binary, tf or tfidf
        """

        self.index = index
        self.term_weighting = term_weighting

        # The total number of documents in the collection |D|
        self.total_doc = max(doc for value in index.values() for doc in value)

        # All the terms that appear in a document
        self.terms_in_doc = {doc: {term for term in [terms for terms, docs in index.items()
                                                     if doc in docs]}
                             for doc in range(1, self.total_doc + 1)}

        if term_weighting == 'tfidf':
            # The number of documents containing a term
            doc_freq = {term: len([doc_freq for doc_freq in self.index[term]])
                        for term in self.index}

    def forQuery(self, query):
        """
        Method performing retrieval for specified query

        :param query: The query to process
        :return: The top 10 most relevant documents to the query
        """

        candidate = self.get_candidate(query)

        similarity = {}

        if self.term_weighting == 'binary':
            """
            Binary weighting scheme

            Term weight is either 0 or 1, easy implementation and weak result
            """

            for doc in candidate:
                query_doc_product = 0
                doc_vec_size = 0

                for term in self.terms_in_doc[doc]:
                    doc_vec_size += 1

                    if term in query:
                        query_doc_product += 1

                similarity[doc] = query_doc_product / math.sqrt(doc_vec_size)

        elif self.term_weighting == 'tf':
            """
            Term frequency weighting scheme

            Term weight depends on its frequency in the specific document, for query,
            the term weight depends on its frequency in the query as well
            """

            for doc in candidate:
                query_doc_product = 0
                doc_vec_size = 0

                for term in self.terms_in_doc[doc]:
                    doc_vec_size += self.index[term][doc] ** 1.95

                    if term in query:
                        query_doc_product += self.index[term][doc] * query[term]

                similarity[doc] = query_doc_product / math.sqrt(doc_vec_size)

        else:
            """
            TFIDF weighting scheme

            Term weight depends on the inverse document frequency (idf), and the
            TFIDF (term frequency * inverse document frequency)
            """

            for doc in candidate:
                query_doc_product = 0
                doc_vec_size = 0

                for term in self.terms_in_doc[doc]:
                    idf = math.log10(self.total_doc / self.doc_freq[term])
                    tfidf = idf * self.index[term][doc]

                    doc_vec_size += tfidf ** 2

                    if term in query:
                        query_doc_product += tfidf * query[term] * idf

                similarity[doc] = query_doc_product / math.sqrt(doc_vec_size)

        ranked_doc = sorted(similarity.items(), key=itemgetter(1), reverse=True)

        return [x[0] for x in ranked_doc[:10]]

    def get_candidate(self, query):
        """
        Get a list of candidate documents that are related to the query

        :param query: The query to search for
        :return: The list of documents that contain at least one same word with query
        """

        candidate_doc = {doc: score
                         for doc in self.terms_in_doc
                         for score in [len(set(query) & self.terms_in_doc[doc])]
                         if score is not 0}

        # Sort according to the candidate 'score'
        candidate_doc = sorted(candidate_doc.items(), key=itemgetter(1), reverse=True)

        return [doc for doc, _ in candidate_doc]
