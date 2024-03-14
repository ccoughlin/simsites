"""
vector_store - utils for simple vector stores (!)
"""
from typing import *
from sklearn.neighbors import NearestNeighbors

from simsites.util.embed import generate_embeddings


class NNVectorStore:
    """
    Basic in-memory vector store, using the Nearest Neighbors algorithm.
    """

    def __init__(self, embed_function: Any = generate_embeddings, **kwargs):
        self._neighbors = NearestNeighbors(
            metric=kwargs.pop('metric', 'cosine'),
            **kwargs
        )
        self.embed_function = embed_function
        self.embeddings = list()
        self.texts = list()

    def fit(self):
        """
        Fits the underlying nearest neighbors vector store.
        :return:
        """
        self._neighbors.fit(self.embeddings)

    def add_texts(self, texts: List[AnyStr]):
        """
        Adds texts to the vector store. Triggers a refit operation.
        :param texts: texts to be added to the vector store.
        :return: None
        """
        if len(texts) > 0:
            self.texts.extend(texts)
            self.embeddings.extend(self.embed_function(texts))
            self.fit()

    def get_relevant_texts(self, query: AnyStr, k: int = 2, t: float = None) -> List[AnyStr]:
        """
        Searches for the most similar texts to a given query.
        :param query: query to match
        :param k: number of nearest results to return (defaults to 2).
        :param t: distance threshold: if specified, only results with a lower distance are returned. Default is None,
        i.e. all results are returned regardless of distance metric.
        :return: list of strings representing the most similar strings to the query in the current vector store. List
        may be empty if no results found or if no results had smaller distances than the target distance specified.
        """
        query_embedding = self.embed_function([query])
        knn_dists, knn_idxs = self._neighbors.kneighbors(X=query_embedding, n_neighbors=k, return_distance=True)
        if t:
            valid_idxs = list()
            for i in range(len(knn_dists[0])):
                if knn_dists[0][i] < t:
                    valid_idxs.append(knn_idxs[0][i])
        else:
            valid_idxs = knn_idxs[0]
        return [self.texts[idx] for idx in valid_idxs]
