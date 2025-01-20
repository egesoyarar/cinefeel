from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import requests
from math import ceil
import pandas as pd

OMDB_API_KEY = ''  # Replace with your OMDb API key
OMDB_BASE_URL = 'http://www.omdbapi.com/'

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database initialization
def init_db():
    conn = sqlite3.connect('cinefeel.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_movie_data():
    df = pd.read_csv('data/movie_data.csv', sep="|")
    return df['movieName'].dropna().tolist()  # Ensure valid movie names

# Endpoint to fetch movies for infinite scrolling
@app.route('/api/movies/<int:page>')
def get_movies(page):
    try:
        MOVIES_PER_PAGE = 12  # Number of movies per page
        all_movies = load_movie_data()
        start_idx = (page - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE

        # Get the current batch of movies
        current_batch = all_movies[start_idx:end_idx]
        movies_data = []

        for movie_name in current_batch:
            response = requests.get(
                OMDB_BASE_URL,
                params={
                    'apikey': OMDB_API_KEY,
                    't': movie_name,  # Search by title
                    'type': 'movie'
                }
            )
            if response.status_code == 200:
                movie_data = response.json()
                if movie_data.get('Response') == 'True':
                    movies_data.append({
                        'title': movie_data.get('Title'),
                        'poster': movie_data.get('Poster') if movie_data.get('Poster') != 'N/A' else None,
                        'year': movie_data.get('Year'),
                        'imdbID': movie_data.get('imdbID')
                    })

        total_pages = ceil(len(all_movies) / MOVIES_PER_PAGE)
        has_more = page < total_pages

        return jsonify({
            'movies': movies_data,
            'hasMore': has_more
        })
    except Exception as e:
        print(f"Error fetching movies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    try:
        # Fetch movies from OMDb API
        response = requests.get(
            OMDB_BASE_URL,
            params={
                'apikey': OMDB_API_KEY,
                's': 'popular',  # Search keyword for popular movies
                'type': 'movie',
                'page': 1
            }
        )
        if response.status_code == 200:
            data = response.json()
            movies = data.get('Search', [])[:12]  # Get the top 12 results
            return render_template('index.html', movies=movies)
        else:
            print(f"Error fetching movies: {response.status_code} - {response.text}")
            return render_template('index.html', movies=[])
    except Exception as e:
        print(f"Error fetching movies: {e}")
        return render_template('index.html', movies=[])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        fullname = data.get('fullname')
        email = data.get('email')
        password = data.get('password')
        
        if not all([fullname, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('cinefeel.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)',
                     (fullname, email, hashed_password))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Registration successful'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Email already exists'}), 400
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        conn = sqlite3.connect('cinefeel.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['fullname'] = user[1]
            return jsonify({'message': 'Login successful'}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
        
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', fullname=session.get('fullname'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
