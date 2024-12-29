# This project is deprecated as Spotify removed the ability to retrieve a user's Discovery Weekly and Release Radar playlists

First time use:
1. Copy config.json.default to config.json
2. Fill in client id and secret
3. Run app.py to get access token cached and saved by signing in to Spotify OAuth

To run in background:
1. Complete previous steps.
2. Build dockerfile image
3. Run "docker compose up -d"