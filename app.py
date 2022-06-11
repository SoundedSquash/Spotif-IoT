from functools import total_ordering
from unittest import result
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import date
import os

scope = 'playlist-modify-private playlist-read-private'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlistFromId = ""
playlistFromName = os.getenv('SPOTIPY_PLAYLIST_TO_EXPORT')
playlistToId = ""
playlistToName = os.getenv('SPOTIPY_PLAYLIST_TO_IMPORT') + str(date.today().year) if os.getenv('SPOTIPY_PLAYLIST_TO_IMPORT_ADD_YEAR') else ''
limit = int(os.getenv('SPOTIPY_PAGE_LIMIT')) if os.getenv('SPOTIPY_PAGE_LIMIT') else 100
offset = -limit

while not playlistFromId and not playlistToId:
    offset += limit
    results = spotify.current_user_playlists(limit=limit, offset=offset)
    # Find playlist and search all playlists for the playlist name
    for playlist in results['items']:
        if(playlist['owner']['id'] == 'spotify' and playlist['name'] == playlistFromName):
            print(playlist['id'])
            playlistFromId = playlist['id']
        if(playlist['name'] == playlistToName):
            print(playlist['id'])
            playlistToId = playlist['id']

if(playlistFromId):
    if(not playlistToId):
        playlistToId = spotify.user_playlist_create(spotify.me()['id'], playlistToName, public=False)['id']
    if(playlistFromId and playlistToId):
        # Get all tracks from playlist
        results = spotify.playlist_tracks(playlist_id=playlistFromId, fields='items.track(id, name)')
        fromTracks = results['items']
        fromTrackIds = list(map(lambda x: x['track']['id'], fromTracks))

        offset = -limit
        toTracks = []
        while True:
            offset += limit
            results = spotify.playlist_tracks(playlist_id=playlistToId, fields='items.track(id, name)', limit=limit, offset=offset)
            if(len(results['items']) == 0):
                break

            if(toTracks): toTracks.extend(results['items'])
            else: toTracks = results['items']

        toTrackIds = list(map(lambda x: x['track']['id'], toTracks))
        uniqueTrackIds = set(set(fromTrackIds) - set(toTrackIds))
        # Add tracks to playlist
        if(len(uniqueTrackIds) > 0): spotify.playlist_add_items(playlist_id=playlistToId, items=uniqueTrackIds)
