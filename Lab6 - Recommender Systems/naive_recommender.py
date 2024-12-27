import pandas as pd 
import utils as ut

def naive_recommender(ratings: object, movies: object, k: int = 10) -> list:
    """
    Recommends movies based on their average rating.

    Args:
        ratings (DataFrame): The input ratings DataFrame containing "movieId" and "rating" columns.
        movies (DataFrame): The input movies DataFrame containing "movieId" and "title" columns.
        k (int): The number of top-rated movies to recommend.

    Returns:
        list: A list of movie IDs representing the recommendations.
    """
    
    # Calculate average rating for each movie
    average_ratings = ratings.groupby('movieId')['rating'].mean()

    # Sort movies by average rating in descending order
    sorted_movies = average_ratings.sort_values(ascending=False)

    # Get the top k movieIds
    top_movie_ids = sorted_movies.head(k).index.tolist()
    
    return top_movie_ids



if __name__ == "__main__":

    path_to_ml_latest_small = 'datasets/'
    dataset = ut.load_dataset_from_source(path_to_ml_latest_small)
    
    ratings, movies = dataset["ratings.csv"], dataset["movies.csv"]
    recommendations = naive_recommender(ratings, movies)
    print(recommendations)