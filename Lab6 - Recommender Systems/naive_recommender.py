import pandas as pd 
import utils as ut

def naive_recommender(ratings: object, movies:object, k: int = 10) -> list: 
    # Provide the code for the naive recommender here. This function should return 
    # the list of the top most viewed films according to the ranking (sorted in descending order).
    # Consider using the utility functions from the pandas library.
    most_seen_movies= []
 
    return most_seen_movies[:k]


if __name__ == "__main__":
    
    path_to_ml_latest_small = '/home/albert/Projects/practica_recomenders/ml-latest-small/'
    dataset = ut.load_dataset_from_source(path_to_ml_latest_small)
    
    ratings, movies = dataset["ratings.csv"], dataset["movies.csv"]
    naive_recommender(ratings, movies)

