import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

#streamlit run app.py

# Replace these with your actual Spotify credentials
CLIENT_ID = "93900cbb4be44d1aacee1c14d9842f3b"
CLIENT_SECRET = "14fb1a98245d45108414340f76e8a6a2"


# Load environment variables
#CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
#CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        track_id = track['id']  # Get the track ID for embedding
        return album_cover_url, track_id
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", None

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    recommended_track_ids = []  # Store track IDs for embedding
    
    for i in distances[1:7]:
        artist = music.iloc[i[0]].artist
        album_cover_url, track_id = get_song_album_cover_url(music.iloc[i[0]].song, artist)
        recommended_music_posters.append(album_cover_url)
        recommended_music_names.append(music.iloc[i[0]].song)
        recommended_track_ids.append(track_id)  # Add track ID to the list

    return recommended_music_names, recommended_music_posters, recommended_track_ids

def search_song(song_name):
    results = sp.search(q=song_name, type="track", limit=6)
    songs = []
    for item in results['tracks']['items']:
        song_info = {
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'album': item['album']['name'],
            'release_date': item['album']['release_date'],
            'cover_url': item['album']['images'][0]['url'],
            'track_id': item['id']  # Get track ID for embedding
        }
        songs.append(song_info)
    return songs

# Streamlit UI
st.title('Music Recommendation System')
st.write("Select a song from the dropdown or search for a song to get recommendations.")

music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Initialize variables for recommendations
recommended_music_names = []
recommended_music_posters = []
recommended_track_ids = []

# Search functionality
# Search functionality
search_query = st.text_input("Enter a song name:")
if st.button("Search"):
    search_results = search_song(search_query)
    if search_results:
        # Display search results in two columns
        st.subheader("Search Results")
        num_results = len(search_results)

        # Custom CSS for the gray blur box
        st.markdown("""
        <style>
        .song-box {
            background-color: rgba(128, 128, 128, 0.4); /* Light gray with opacity */
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
        }
        .song-box img {
            border-radius: 5px;
        }
        .song-box iframe {
            border-radius: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Arrange search results into 2 columns
        for i in range(0, num_results, 2):
            cols = st.columns(2)  # Create two columns
            if i < num_results:
                with cols[0]:
                    # Display image, name, and embed in a gray blur box
                    st.markdown(f"""
                        <div class="song-box">
                            <a href="https://open.spotify.com/track/{search_results[i]['track_id']}" target="_blank">
                                <img src="{search_results[i]['cover_url']}" width="300" height="250"/>
                            </a>
                            <p><strong>{search_results[i]['name']}</strong> by <em>{search_results[i]['artist']}</em></p>
                            <iframe src="https://open.spotify.com/embed/track/{search_results[i]['track_id']}" width="300" height="80" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                            <p>*Album: {search_results[i]['album']}* | *Released: {search_results[i]['release_date']}*</p>
                        </div>
                    """, unsafe_allow_html=True)

            if i + 1 < num_results:  # To ensure we don't go out of bounds
                with cols[1]:
                    # Display image, name, and embed in a gray blur box
                    st.markdown(f"""
                        <div class="song-box">
                            <a href="https://open.spotify.com/track/{search_results[i+1]['track_id']}" target="_blank">
                                <img src="{search_results[i+1]['cover_url']}" width="300" height="250"/>
                            </a>
                            <p><strong>{search_results[i+1]['name']}</strong> by <em>{search_results[i+1]['artist']}</em></p>
                            <iframe src="https://open.spotify.com/embed/track/{search_results[i+1]['track_id']}" width="300" height="80" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                            <p>*Album: {search_results[i+1]['album']}* | *Released: {search_results[i+1]['release_date']}*</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.write("No results found.")

  
# Recommendation dropdown
# Recommendation dropdown
music_list = music['song'].values
selected_song = st.selectbox("Or select a song", music_list)

if st.button('Show Recommendation'):
    with st.spinner("Generating recommendations..."):
        recommended_music_names, recommended_music_posters, recommended_track_ids = recommend(selected_song)

    # Display recommendations in two columns
    st.subheader("Recommended Songs")
    num_recommendations = len(recommended_music_names)

    # Custom CSS for the gray blur box
    st.markdown("""
    <style>
    .song-box {
        background-color: rgba(128, 128, 128, 0.4); /* Light gray with opacity */
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .song-box img {
        border-radius: 5px;
    }
    .song-box iframe {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Arrange recommendations into 2 columns
    for i in range(0, num_recommendations, 2):
        cols = st.columns(2)  # Create two columns
        if i < num_recommendations:
            with cols[0]:
                # Display image, name, and embed in a gray blur box
                st.markdown(f"""
                    <div class="song-box">
                        <a href="https://open.spotify.com/track/{recommended_track_ids[i]}" target="_blank">
                            <img src="{recommended_music_posters[i]}" width="300" height="250"/>
                        </a>
                        <p><strong>{recommended_music_names[i]}</strong></p>
                        <iframe src="https://open.spotify.com/embed/track/{recommended_track_ids[i]}" width="300" height="80" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    </div>
                """, unsafe_allow_html=True)

        if i + 1 < num_recommendations:  # To ensure we don't go out of bounds
            with cols[1]:
                # Display image, name, and embed in a gray blur box
                st.markdown(f"""
                    <div class="song-box">
                        <a href="https://open.spotify.com/track/{recommended_track_ids[i+1]}" target="_blank">
                            <img src="{recommended_music_posters[i+1]}" width="300" height="250"/>
                        </a>
                        <p><strong>{recommended_music_names[i+1]}</strong></p>
                        <iframe src="https://open.spotify.com/embed/track/{recommended_track_ids[i+1]}" width="300" height="80" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    </div>
                """, unsafe_allow_html=True)

# User feedback section
st.subheader("Provide Feedback")
if recommended_music_names:  # Check if recommendations have been generated
    feedback_song = st.selectbox("Select a song for feedback", recommended_music_names)
    feedback = st.radio("Did you like this song?", ('👍 Yes', '👎 No'))

    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
else:
    st.write("Please generate recommendations first to provide feedback.")

# Optional: Add an about section
st.sidebar.header("About")
st.sidebar.markdown(
    """
    This app recommends songs based on your selection using the Spotify API and a recommendation model. 
    You can either search for a song or select one from the dropdown to see similar tracks. 
    Enjoy music recommendations and explore new artists!
    """
)