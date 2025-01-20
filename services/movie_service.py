import pandas as pd
from config.config import OMDB_API_KEY, MOVIES_PER_PAGE
import requests

class MovieService:
    @staticmethod
    def load_movie_data():
        df = pd.read_csv('data/movie_data.csv', sep="|")
        return df['movieName'].tolist()

    @staticmethod
    def get_movies_page(page):
        all_movies = MovieService.load_movie_data()
        start_idx = (page - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE
        
        current_batch = all_movies[start_idx:end_idx]
        return MovieService.fetch_movie_details(current_batch)

    @staticmethod
    def fetch_movie_details(movie_names):
        movies_data = []
        for movie_name in movie_names:
            response = requests.get(
                'http://www.omdbapi.com/',
                params={
                    'apikey': OMDB_API_KEY,
                    't': movie_name,
                    'type': 'movie'
                }
            )
            if response.status_code == 200:
                movie_data = response.json()
                if movie_data.get('Response') == 'True':
                    movies_data.append({
                        'title': movie_data.get('Title'),
                        'poster': movie_data.get('Poster'),
                        'year': movie_data.get('Year'),
                        'rating': movie_data.get('imdbRating', 'N/A')
                    })
        return movies_data 