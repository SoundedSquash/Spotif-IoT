import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import date
from pathlib import Path

#Load config
config = json.load(open(Path(__file__).with_name('config.json')))

scope = 'playlist-modify-private playlist-read-private'
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['clientId'], client_secret=config['clientSecret'], redirect_uri=config['redirectUrl'], scope=scope))

limit = int(config['resultLimit']) if config['resultLimit'] else 50

copyTracks = config["copyTracks"]


# >> IMPORTANT << Before debugging why it's not adding tracks, please check the playlist from another device to make sure it's really not there. I've experienced desktop not showing the new tracks for some reason.
def CopyTracks(playlistFromName, playlistToName, addYeartoPlaylistToName):
    playlistToName += str(date.today().year) if addYeartoPlaylistToName else ''
    offset = -limit
    playlistFromId = ""
    playlistToId = ""

    while not playlistFromId and not playlistToId:
        offset += limit
        results = spotify.current_user_playlists(limit=limit, offset=offset)
        # Find playlist and search all playlists for the playlist name
        for playlist in results['items']:
            if(playlist['name'] == playlistFromName):
                playlistFromId = playlist['id']
                print(f"Found From playlist '{playlistFromName}'")
            if(playlist['name'] == playlistToName):
                playlistToId = playlist['id']
                print(f"Found To playlist '{playlistToName}'")

    if(playlistFromId):
        if(not playlistToId):
            print(f"Playlist does not exist. Attempting to create it.")
            playlistToId = spotify.user_playlist_create(spotify.me()['id'], playlistToName, public=False)['id']
        if(playlistFromId and playlistToId):
            # Get all tracks from playlist (limit 100 by default)
            results = spotify.playlist_tracks(playlist_id=playlistFromId, fields='items.track(id, name)')
            fromTracks = results['items']

            # offset gets incremented at start of loop. Make it negative so it increments to start at 0.
            offset = -limit
            toTracks = []
            while True:
                offset += limit
                results = spotify.playlist_tracks(playlist_id=playlistToId, fields='items.track(id, name)', limit=limit, offset=offset)
                if(len(results['items']) == 0):
                    print(f"Loaded all tracks in playlist.")
                    break
                
                if(toTracks): toTracks.extend(results['items'])
                else: toTracks = results['items']
                print(f"Loaded tracks {offset + 1} to {offset + limit}.")


            print(f"Determining if there are new tracks to add.")
            # Find tracks ids that are missing from the To playlist by comparing the lists.
            uniqueTrackIds = [track['track']['id'] for track in fromTracks if track['track']['id'] not in [item['track']['id'] for item in toTracks]]
            # Add tracks to playlist
            if(len(uniqueTrackIds) > 0): 
                spotify.playlist_add_items(playlist_id=playlistToId, items=uniqueTrackIds)
                print(f"Adding {len(uniqueTrackIds)} tracks to {playlistToName}")
            else: 
                print(f"No tracks to add.")
        else: #if(playlistFromId and playlistToId)
            raise SystemExit(f"Playlist From and/or Playlist To not found. From: '{playlistFromId}' To: {playlistToId}")
    else: # if(playlistFromId)
        raise SystemExit(f"Playlist From '{playlistFromName}' not found")

for copyTrack in copyTracks:
    CopyTracks(copyTrack["playlistFromName"], copyTrack["playlistToName"], copyTrack["addCurrentYearToPlaylistToName"])