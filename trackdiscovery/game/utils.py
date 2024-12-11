import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect
from django.conf import settings


def get_access_token(request):
    # Retrieve the access token from session
    access_token = request.session.get('access_token')
    refresh_token = request.session.get('refresh_token')

    if access_token:
        # Check if the token is expired
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIPY_REDIRECT_URI,
            scope="user-top-read"
        )
        token_info = sp_oauth.validate_token(access_token)
        if token_info['expires_in'] <= 0 and refresh_token:
            # If the access token is expired and refresh token exists, refresh the token
            token_info = sp_oauth.refresh_access_token(refresh_token)
            request.session['access_token'] = token_info['access_token']
            request.session['refresh_token'] = token_info['refresh_token']
            return token_info['access_token']
        return access_token
    return None  # No valid token found


def getSpotifyClient(request, token=None):
    if token:
        return spotipy.Spotify(auth=token)

    # Try to get the access token from the session
    access_token = get_access_token(request)

    if access_token:
        return spotipy.Spotify(auth=access_token)

    # If no token is available, redirect to the Spotify authentication URL
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotifyCallback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )

    code = request.GET.get('code')
    if not code:
        return redirect('game:spotifyLogin')

    token_info = sp_oauth.get_access_token(code)

    # Save the token in the user's session
    request.session['access_token'] = token_info['access_token']
    return redirect('game:play')

def getUserTopArtists(request, difficulty, limit=10):
    token = request.session.get('access_token')
    if not token:
        return redirect('game:spotifyLogin')

    sp = getSpotifyClient(token)

    time_ranges = {
        "Easy": 'short_term',
        "Normal": 'medium_term',
        "Hard": 'long_term'
    }
    time_range = time_ranges.get(difficulty, 'medium_term')

    results = sp.current_user_top_artists(limit=limit, time_range=time_range)
    print("Top Artists Results:", results)

    return {artist['name']: artist['id'] for artist in results.get('items', [])}

def fetchSongsFromArtist(artist_id, token):
    sp = getSpotifyClient(token)
    results = sp.artist_top_tracks(artist_id)

    return [
        {"name": track['name'], "preview_url": track['preview_url']}
        for track in results.get('tracks', [])
        if track['preview_url']
    ]

def fetchAlbumArtFromArtist(artist_id, token):
    sp = getSpotifyClient(token)
    results = sp.artist_albums(artist_id, album_type='album', limit=10)

    return [
        {"name": album['name'], "image_url": album['images'][0]['url']}
        for album in results.get('items', [])
        if album['images']
    ]

def getRandomArtistSnippet(request, difficulty):
    # Ensure the user has an access token
    access_token = request.session.get('access_token')
    if not access_token:
        print("Error: No access token found")
        return None

    # Create a Spotipy client
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch top artists based on the difficulty level
        time_ranges = {
            "Easy": 'short_term',
            "Normal": 'medium_term',
            "Hard": 'long_term'
        }
        time_range = time_ranges.get(difficulty, 'medium_term')

        results = sp.current_user_top_artists(limit=10, time_range=time_range)
        print("Fetched top artists:", results)

        if not results['items']:
            print("Error: No artists found")
            return None

        # Pick a random artist from the list
        artist = random.choice(results['items'])
        print("Selected artist:", artist['name'])

        # Fetch top tracks for the selected artist
        track_results = sp.artist_top_tracks(artist['id'])
        print("Fetched top tracks for artist:", track_results)

        # Check if the artist has tracks with a preview URL
        tracks_with_preview = [track for track in track_results['tracks'] if track['preview_url']]
        if not tracks_with_preview:
            print("Error: No tracks with preview URLs found")
            return None

        # Pick a random track with a preview URL
        track = random.choice(tracks_with_preview)
        snippet_data = {
            'track_name': track['name'],
            'artist': artist['name'],
            'preview_url': track['preview_url']
        }
        return snippet_data

    except Exception as e:
        print(f"Error fetching snippet: {e}")
        return None


def getRandomArtistAlbum(request, difficulty):
    # Ensure the user has an access token
    access_token = request.session.get('access_token')
    if not access_token:
        print("Error: No access token found")
        return None

    # Create a Spotipy client
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Difficulty based
        if difficulty == 'Easy':
            limit = 3
        elif difficulty == 'Normal':
            limit = 5
        elif difficulty == 'Hard':
            limit = 10

        # Fetch top artist albums
        results = sp.current_user_top_artists(limit=limit)

        if not results['items']:
            print("Error: No artists found")
            return None

        album_data_list = []

        for artist in results['items']:
            # Fetch albums for each selected artist
            album_results = sp.artist_albums(artist['id'], limit=limit)
            print(f"Fetched albums for artist: {artist['name']}", album_results)

            if album_results['items']:
                # Pick a random album from the artist's albums
                album = random.choice(album_results['items'])
                album_data_list.append({
                    'image_url': album['images'][0]['url'] if album['images'] else '',
                    'artist': artist['name']
                })

        return album_data_list

    except Exception as e:
        print(f"Error fetching album: {e}")
        return None
