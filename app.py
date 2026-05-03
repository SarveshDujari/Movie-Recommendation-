import streamlit as st
import pickle
import pandas as pd
import requests

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

  /* Dark cinematic background */
  .stApp {
    background: radial-gradient(ellipse at top, #1a1a2e 0%, #0d0d0d 60%);
    color: #f0ece2;
  }

  /* Title */
  h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 3.8rem !important;
    letter-spacing: 6px !important;
    color: #f5c518 !important;  /* IMDb gold */
    text-shadow: 0 0 40px rgba(245,197,24,0.3);
    text-align: center;
    margin-bottom: 0.2rem !important;
  }

  .subtitle {
    text-align: center;
    font-family: 'DM Sans', sans-serif;
    color: #888;
    font-size: 0.95rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
  }

  /* Selectbox */
  .stSelectbox > div > div {
    background: #1c1c1c !important;
    border: 1px solid #f5c518 !important;
    border-radius: 8px !important;
    color: #f0ece2 !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* Recommend button */
  .stButton > button {
    background: #f5c518 !important;
    color: #0d0d0d !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important;
    letter-spacing: 3px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2.5rem !important;
    width: 100%;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(245,197,24,0.25) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(245,197,24,0.45) !important;
  }

  /* Movie cards */
  .movie-card {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    background: #1c1c1c;
  }
  .movie-card:hover {
    transform: scale(1.05) translateY(-6px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.7), 0 0 20px rgba(245,197,24,0.2);
  }
  .movie-card img {
    width: 100%;
    border-radius: 12px 12px 0 0;
    display: block;
  }
  .movie-info {
    padding: 10px 12px 14px;
    background: linear-gradient(0deg, #111 0%, #1c1c1c 100%);
  }
  .movie-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    color: #f0ece2;
    margin: 0 0 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .stars {
    color: #f5c518;
    font-size: 0.78rem;
    letter-spacing: 2px;
  }

  /* Divider */
  .gold-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #f5c518, transparent);
    margin: 2rem 0;
  }

  /* Section label */
  .rec-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 4px;
    color: #f5c518;
    text-align: center;
    margin-bottom: 1.2rem;
  }
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────
def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=d55f6af710a6c3762bf85e38a43bc42f&language=en-US'.format(movie_id))
    data = response.json()
    print(data)
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index
    distances = similarity[movie_index][0]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters


def render_movie_card(title, poster_url):
    """Render a styled HTML movie card."""
    import random
    stars = "★" * random.randint(3, 5) + "☆" * (5 - random.randint(3, 5))
    st.markdown(f"""
    <div class="movie-card">
      <img src="{poster_url}" alt="{title}">
      <div class="movie-info">
        <p class="movie-title">{title}</p>
        <div class="stars">{stars}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("<h1>🎬 CineMatch</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover your next obsession</p>', unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    selected_movie_name = st.selectbox(
        "Pick a movie you love:",
        movies['title'].values,
        label_visibility="collapsed"
    )
    clicked = st.button("✦  Find My Movies  ✦")

if clicked:
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.markdown('<p class="rec-label">Because you watched...</p>', unsafe_allow_html=True)

    # Animated spinner while fetching
    with st.spinner("🎞️ Rolling the reel..."):
        names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            render_movie_card(name, poster)