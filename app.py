from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from services.movie_service import MovieService
from config.config import SECRET_KEY, MOVIES_PER_PAGE
from math import ceil

app = Flask(__name__)
app.secret_key = SECRET_KEY

movie_service = MovieService()

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/login')
def login():
    return render_template('pages/login.html')

@app.route('/signup')
def signup():
    return render_template('pages/signup.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pages/profile.html')

@app.route('/api/movies')
def get_movies():
    page = request.args.get('page', 1, type=int)
    try:
        movies = movie_service.get_movies_page(page)
        total_movies = len(movie_service.load_movie_data())
        total_pages = ceil(total_movies / MOVIES_PER_PAGE)
        
        return jsonify({
            'movies': movies,
            'hasMore': page < total_pages
        })
    except Exception as e:
        print(f"Error in get_movies: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)