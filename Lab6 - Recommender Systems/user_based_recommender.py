import pandas as pd
import numpy as np

import similarity as sim
import naive_recommender as nav
import utils as ut


def generate_m(ratings, movies):
    """
    Generates a user-movie rating matrix using optimized pivot operation.
    """
    return ratings.pivot(index="userId", columns="movieId", values="rating")


def user_based_recommender(target_user_id, matrix, top_n=10, consider_genres=False, genre_matrix=None):
    """
    Generates movie recommendations for a target user using user-based collaborative filtering.
    Includes optimizations for similarity computation and optional genre consideration.
    """

    # Get the target user's ratings
    target_user = matrix.loc[target_user_id]

    # Pre-calculate user means for efficiency
    user_means = matrix.mean(axis=1).fillna(0)

    # Calculate similarities to other users (using only commonly rated movies)
    similarities = matrix.corrwith(target_user, axis=1, method=sim.compute_similarity) 
    similarities.dropna(inplace=True)  # Remove users with no similarity
    similarities.sort_values(ascending=False, inplace=True)
    similarities = similarities.drop(target_user_id)  # Remove the target user itself

    # If no similar users, return an empty list
    if similarities.empty:
        print(f"No similar users found for user {target_user_id}")
        return []

    # Get unseen movies
    unseen_movies = target_user[target_user.isna()].index

    # Generate recommendations
    recommendations = []
    for movie_id in unseen_movies:
        # Users who rated the movie and are similar to the target user
        users_rated_movie = matrix[movie_id].dropna()
        similar_users_rated_movie = users_rated_movie[users_rated_movie.index.isin(similarities.index)]

        # Weighted average of ratings, adjusted by user means
        weighted_ratings = (
            similarities[similar_users_rated_movie.index]
            * (similar_users_rated_movie - user_means[similar_users_rated_movie.index])
        ).sum()
        similarity_sum = np.abs(similarities[similar_users_rated_movie.index]).sum()

        if similarity_sum > 0:
            predicted_rating = user_means[target_user_id] + (weighted_ratings / similarity_sum)
            recommendations.append((movie_id, predicted_rating))

    # Sort by predicted rating
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # Filter by genre if needed
    if consider_genres and genre_matrix is not None:
        recommendations = filter_by_genre_preferences(target_user_id, recommendations, genre_matrix, top_n)

    return recommendations[:top_n]

def filter_by_genre_preferences(target_user_idx, recommendations, genre_matrix, top_n):
    """
    Filters recommendations based on the target user's most-watched genres.
    """
    # Obtener los géneros más vistos por el usuario
    user_genres = genre_matrix.loc[target_user_idx].sort_values(ascending=False)

    # Filtrar películas que coincidan con los géneros más vistos
    filtered_recommendations = []
    for movie_id, predicted_rating in recommendations:
        movie_genres = genre_matrix.loc[movie_id]
        if any(movie_genres & user_genres):  # Si hay coincidencias de género
            filtered_recommendations.append((movie_id, predicted_rating))
        if len(filtered_recommendations) == top_n:
            break

    return filtered_recommendations
