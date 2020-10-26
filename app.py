import authorization
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    authorization_url = authorization.Authorization().get_authorize()
    return render_template('index.html', auth_url=authorization_url)

@app.route('/dashboard')
def dashbord():
    auth_code = request.args.get('code')
    spotify = authorization.Authorization()
    spotify.set_code(auth_code)
    spotify.get_token()
    generate_playlist = spotify.generate_playlist()
    return render_template('dashboard.html', playlist_url=generate_playlist)

if __name__ == '__main__':
    app.run()