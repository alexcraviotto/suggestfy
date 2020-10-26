import requests
import json
import base64
from urllib.parse import urlencode
import datetime
import secrets


class Authorization():
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.client_id = secrets.client_id
        self.client_secret = secrets.client_secret
        self.redirect_uri = secrets.redirect_uri
        self.base_authorize_url = 'https://accounts.spotify.com/authorize'
        self.base_token_url = 'https://accounts.spotify.com/api/token'
        self.authorization_header = {}
        self.auth_code = None
        self.track_seeds = None

    def get_authorize(self):
        authorize_params = urlencode({
        'client_id':self.client_id,
        'response_type':'code',
        'scope': 'user-top-read  playlist-modify-public playlist-modify-private user-read-private user-read-email',
        'redirect_uri': self.redirect_uri
        })
        authorization_url = self.base_authorize_url + '?' + authorize_params
        return authorization_url

    def get_client_credentials(self):
        client_creds = f'{self.client_id}:{self.client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode()) 
        return client_creds_b64

    def get_token_header(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64.decode()}"
        }

    def set_code(self, auth_code):
        self.auth_code = auth_code
        return auth_code
    

    def get_token(self):
        token_data = {
        'grant_type': 'authorization_code',
        'code': self.auth_code,
        'redirect_uri': self.redirect_uri,
        'client_id': self.client_id,
        'client_secret': self.client_secret
        }

        authorization_header = self.get_token_header()
        token_request = requests.post(self.base_token_url, data=token_data, headers=authorization_header)
        print(token_request)
        valid_token_request = token_request.status_code in range(200, 299)
        if valid_token_request:
            token_response_data = token_request.json()
            access_token = token_response_data['access_token']
            refresh_token = token_response_data['refresh_token']
            expires_in = token_response_data['expires_in']
            self.expires_in = expires_in
            self.refresh_token = refresh_token
            self.access_token = access_token
            now = datetime.datetime.now()
            expires = now + datetime.timedelta(seconds=expires_in)
            did_expires = expires > now
            if did_expires:
                return access_token
            else:
                print('token expired... refreshing the token')
                return refresh_token
        else: 
            print("Error in the request validation")

    def get_resource_header(self):
        access_token = self.get_token()
        authorization_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        return authorization_header


    def get_favorite_tracks(self):
        tracks = []
        position = 0
        favorite_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
        authorization_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }        
        favorite_tracks_params = {
            'limit': 5,
            'offset': 0,
            'time_range': 'medium_term'
        }
        favorite_tracks_request = requests.get(favorite_tracks_url, params=favorite_tracks_params, headers=authorization_header)
        result_favorite_tracks_request = favorite_tracks_request.json()
        while position <= 4:
            tracks.append(result_favorite_tracks_request['items'][position]['id'])
            position += 1
        tracks = ','.join(tracks)
        return tracks


    def recommendations(self):
        track_number = 0
        tracks = []
        recommendations_url = 'https://api.spotify.com/v1/recommendations'
        # authorization_header = self.get_resource_header()        
        authorization_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        track_seeds = self.get_favorite_tracks()
        recommendations_params = {
            'limit': 51,
            'seed_tracks': track_seeds
        }
        recommendations_request = requests.get(recommendations_url, params=recommendations_params, headers=authorization_header)
        result_recommendations_request = recommendations_request.json()
        while track_number < 50:
            tracks.append(result_recommendations_request['tracks'][track_number]['uri']) 
            track_number += 1
        return tracks

    def get_user_id(self):
        user_data_url = 'https://api.spotify.com/v1/me'
        authorization_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        user_data_request = requests.get(user_data_url, headers=authorization_header)
        result_user_data_request = user_data_request.json()
        user_id = result_user_data_request['id']
        return user_id

    def generate_playlist(self):
        user_id = self.get_user_id()
        create_playlist_url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        authorization_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        create_playlist_data = {
            'name': 'SuggestFy Playlist',
            'description': 'Playlist generated according to your tastes for suggestfy.com',
            'public': 'false'
        }
        create_playlist_request = requests.post(create_playlist_url, json=create_playlist_data ,headers=authorization_header)
        result_create_playlist_request = create_playlist_request.json()
        playlist_id = result_create_playlist_request['id']
        playlist_url = result_create_playlist_request['external_urls']['spotify']
        add_tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        authorization_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        add_tracks_data = {
            'uris': self.recommendations(),
            'position': 0
        }
        add_tracks_request = requests.post(add_tracks_url, json=add_tracks_data, headers=authorization_header)
        print(add_tracks_request.json())
        return playlist_url









    