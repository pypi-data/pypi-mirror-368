import numpy as np
import scipy as sp
from sklearn.base import BaseEstimator
from recsys_pipeliner.recommendations.transformer import (
    SimilarityTransformer,
)


class SimilarityRecommender(BaseEstimator):
    """Similarity recommender.

    Args:
        n (int): Number of recommendations to generate.
    """

    n: int
    similarity_matrix: sp.sparse.sparray

    def __init__(self, n=5):
        self.n = n

    def fit(self, X, y=None):
        """Fits the recommender to the given data.

        Args:
            X sp.sparse.sparray:
                similarity matrix

        Returns:
            self: Returns the instance itself.

        Raises:
            ValueError: If input is not a scipy.sparse.sparray
        """
        if isinstance(X, sp.sparse.sparray):
            self.similarity_matrix = X
        else:
            raise ValueError("Input should be scipy.sparse.sparray")

        return self

    def _get_recommendations(self, id) -> np.array:
        item_similarity = self.similarity_matrix[[id], :].toarray()
        mask = (item_similarity > 0) * (np.arange(item_similarity.size) != id)
        sorter = np.argsort(1 - item_similarity, kind="stable")
        sorted_mask = mask[0, sorter]
        return sorter[sorted_mask][: self.n]

    def recommend(self, X) -> list[np.array]:
        """Predicts n recommendations for each id provided

        Args:
          X (Sequence): List of id

        Returns:
          list of np.array
        """
        return [self._get_recommendations(id) for id in X]

    def predict_proba(self, X):
        return self.similarity_matrix[X]


class UserBasedRecommender(BaseEstimator):
    """User-based collaborative filtering recommender.

    Args:
        n (int): Number of recommendations to generate for each user
        k (int): Number of similar users to consider for recommendations
    """

    n: int
    k: int

    def __init__(self, n=5, k=5, exp=1e-6, debias=False):
        self.n = n
        self.k = k
        self.exp = exp
        self.debias = debias
        self._user_transformer = SimilarityTransformer()

    def fit(self, X: sp.sparse.sparray, y=None):
        """Fits the recommender to the given data.

        Args:
            X sp.sparse.sparray:
                user/item matrix

        Returns:
            self: Returns the instance itself.

        Raises:
            ValueError: If input is not a scipy.sparse.sparray
        """
        if isinstance(X, sp.sparse.sparray):
            self._user_item_matrix = X
            self._user_similarity_matrix = self._user_transformer.transform(X)
        else:
            raise ValueError("Input should be scipy.sparse.sparray")

        return self

    def _get_similar_users(self, id: int) -> np.array:
        matrix = self._user_similarity_matrix[[id]]
        user_mask = matrix > 0
        user_mask[[0], [id]] = False
        user_sorter = np.argsort(1 - matrix.toarray()[0], kind="stable")
        sorted_mask = user_mask.toarray()[0][user_sorter]
        similar_users = user_sorter[sorted_mask][: self.k]

        return similar_users

    def _get_exclusions(self, id: int) -> np.array:
        single_user_ratings = self._user_item_matrix[[id]]
        rated = (single_user_ratings > 0).nonzero()[1]
        return rated

    def _get_recommendations(self, id: int) -> np.array:
        excluded_items = self._get_exclusions(id)
        similar_users = self._get_similar_users(id)

        matrix = self._user_item_matrix[similar_users]

        any_ratings = np.nonzero(matrix.sum(axis=0))[0]
        items_to_use = np.setdiff1d(any_ratings, excluded_items)

        filtered_matrix = matrix[:, items_to_use]

        mean_ratings = filtered_matrix.toarray().T.mean(axis=1)
        item_sorter = np.argsort(1 - mean_ratings, kind="stable")

        return items_to_use[item_sorter][: self.n]

    def recommend(self, X) -> list[np.array]:
        """Predicts n recommendations for each id provided

        Args:
          X (Sequence): List of id

        Returns:
          list of np.array
        """
        return [self._get_recommendations(id) for id in X]

    def predict(self, user_id: int, item_id: int) -> np.float32:
        _, users, users_ratings = sp.sparse.find(self._user_item_matrix[:, item_id])

        # get the similarities to user_id
        _, _, user_similarities = sp.sparse.find(
            self._user_similarity_matrix[user_id, users]
        )

        # sort by similarity (desc) and get top k
        top_k_mask = np.argsort(1 - user_similarities)[1 : self.k + 1]

        if top_k_mask.shape[0] == 0:
            # no similar users
            return None

        top_k_users_ratings = users_ratings[top_k_mask]
        top_k_users_similarities = np.where(
            user_similarities[top_k_mask] > 0,
            user_similarities[top_k_mask],
            user_similarities[top_k_mask] + self.exp,
        )

        # weighted average rating
        predicted_score = (
            np.average(top_k_users_ratings, axis=0, weights=top_k_users_similarities)
            .astype(np.float32)
            .round(6)
        )
        return predicted_score


class ItemBasedRecommender(BaseEstimator):
    """Item-based collaborative filtering recommender.

    Args:
        n (int): Number of recommendations to generate
        k (int): Number of similar items to consider for recommendations
    """

    n: int
    k: int

    def __init__(self, n=5, k=5, exp=1e-6, debias=False):
        self.n = n
        self.k = k
        self.exp = exp
        self.debias = debias

    def fit(self, X: sp.sparse.sparray, y=None):
        """Fits the recommender to the given data.

        Args:
            X sp.sparse.sparray:
                user/item matrix

        Returns:
            self: Returns the instance itself.

        Raises:
            ValueError: If input is not a scipy.sparse.sparray
        """
        if isinstance(X, sp.sparse.sparray):
            self._user_item_matrix = X
        else:
            raise ValueError("Input should be scipy.sparse.sparray")

        # TODO: broadcasting returns np.array
        # if self.debias:
        #     self.biases = self._user_item_matrix.mean(axis=0)[np.newaxis, :]
        #     self._user_item_matrix -= self.biases

        self._item_similarity_matrix = SimilarityTransformer().transform(
            self._user_item_matrix.T
        )

        return self

    def _get_recommendations(self, id: int) -> np.array:
        item_similarity = self._item_similarity_matrix[[id], :].toarray()
        mask = (item_similarity > 0) * (np.arange(item_similarity.size) != id)
        sorter = np.argsort(1 - item_similarity, kind="stable")
        sorted_mask = mask[0, sorter]
        return sorter[sorted_mask][: self.n]

    def recommend(self, X) -> list[np.array]:
        """Predicts n recommendations for each id provided

        Args:
          X (Sequence): List of id

        Returns:
          list of np.array
        """
        return [self._get_recommendations(id) for id in X]

    def predict(self, user_id: int, item_id: int) -> np.float32:
        _, users_rated_items, users_ratings = sp.sparse.find(
            self._user_item_matrix[user_id, :]
        )
        # get the similarities to item_id
        item_similarities = (
            self._item_similarity_matrix[:, users_rated_items][item_id]
            .toarray()
            .astype(np.float32)
            .round(6)
        )

        # sort by similarity (desc) and get top k
        top_k_mask = np.argsort(1 - item_similarities)[1 : self.k + 1]

        if top_k_mask.shape[0] == 0:
            # no similar items
            return None

        top_k_user_ratings = users_ratings[top_k_mask]
        top_k_rated_item_similarities = np.where(
            item_similarities[top_k_mask] > 0,
            item_similarities[top_k_mask],
            item_similarities[top_k_mask] + self.exp,
        )

        # weighted average rating
        predicted_score = (
            np.average(
                top_k_user_ratings, axis=0, weights=top_k_rated_item_similarities
            )
            .astype(np.float32)
            .round(6)
        )
        return predicted_score
