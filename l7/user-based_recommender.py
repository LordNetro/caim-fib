import pandas as pd
import numpy as np

import similarity as sim
import naive_recommender as nav
import utils as ut


def generate_m(movies_idx, users, ratings):
    # Complete the datastructure for rating matrix 
    # @TODO 
    
    m = None

    
    
    return m 


def user_based_recommender(target_user_idx, matrix):
    target_user = matrix.iloc[target_user_idx]
    recommendations = []
    
    # Compute the similarity between  the target user and each other user in the matrix. 
    # We recomend to store the results in a dataframe (userId and Similarity)
    # @TODO 

    
    # Determine the unseen movies by the target user. Those films are identfied 
    # since don't have any rating. 
    # @TODO 
     
    # Generate recommendations for unrated movies based on user similarity and ratings.
    # @ TODO 
    
    return recommendations



if __name__ == "__main__":
    
    # Load the dataset
    path_to_ml_latest_small = '/home/albert/Projects/practica_recomenders/ml-latest-small/'
    dataset = ut.load_dataset_from_source(path_to_ml_latest_small)

    # Ratings data
    val_movies = 5
    ratings_train, ratings_val = ut.split_users(dataset["ratings.csv"], val_movies)

    # Create matrix between user and movies 
    movies_idx = dataset["movies.csv"]["movieId"]
    users_idy = list(set(ratings_train["userId"].values))
    m = generate_m(movies_idx, users_idy, ratings_train)
        
    # user-to-user similarity
    target_user_idx = 123
    recommendations = user_based_recommender(target_user_idx, m)
     
    # The following code print the top 5 recommended films to the user
    for recomendation in recommendations[:5]:
        rec_movie = dataset["movies.csv"][dataset["movies.csv"]["movieId"]  == recomendation[0]]
        print (" Recomendation :Movie:{} (Genre: {})".format(rec_movie["title"].values[0], rec_movie["genres"].values[0]))

    
    # Validation
    matrixmpa_genres = ut.matrix_genres(dataset["movies.csv"])
    
     
    








