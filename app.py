from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json
import base64
import time
import datetime
from urllib.parse import urlencode
from spotifysearch import SpotifyAPI
import pandas as pd
from QuantiFiRadio import findSong
import os


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'shhh'

client_id = '92ff5487c06344be83ecc3f79b8bbd31'
client_secret = '5050b7d5bda342cba68c4bec2913d669'

client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())


class MyForm(FlaskForm):
    search = StringField('ex: Uptown Funk', validators=[DataRequired()])

class Submit(FlaskForm):
    submit = SubmitField(label = 'submit')

     
@app.route("/", methods = ['GET'])
def index():
    form = MyForm()
    return render_template('index.html', form = form)  

@app.route("/", methods = ['POST'])
def indexPost():
    form = MyForm()
    if form.validate_on_submit():
        data = form.data["search"]
        return redirect(url_for('select', data = data))

@app.route('/select', methods = ['GET'])
def select():
    search = request.args.get('data')
    spotify = SpotifyAPI(client_id, client_secret)
    results = spotify.search(search, search_type = "track")
    items = results["tracks"]["items"]

    song_list = [] 
    id_list = []
    artist_list = []
    artist_id_list = []

    for item in items:
        song_list.append(item["name"])
        id_list.append(item["id"])
        artist_list.append(item["artists"][0]["name"])
        artist_id_list.append(item["artists"][0]["id"])

    return render_template('select.html', song_list = song_list, id_list = id_list, artist_list=artist_list, artist_id_list = artist_id_list)


@app.route('/select', methods = ['POST'])
def selectForm():
    if request.method == 'POST':
        values = request.form.to_dict()
        print(values)
        selection = values['selection']
        x = selection.split(",")
        song_id = x[0]
        artist = x[1]
        artist_id = x[2]
        return redirect(url_for('results', song_id = song_id, artist=artist, artist_id = artist_id))

@app.route('/results', methods = ['GET'])
def results():

    song_id = str(request.args.get('song_id'))
    artist_name = str(request.args.get('artist'))
    artist_id = str(request.args.get('artist_id'))
    spotify = SpotifyAPI(client_id, client_secret)

    #elements outputted to webpage
    audioinfo = spotify.audioinfo(song_id)
    trackinfo = spotify.trackinfo(song_id)
    artistinfo = spotify.artistinfo(artist_id)

    song_name = trackinfo["name"]
    popularity = trackinfo["popularity"]
    genres = artistinfo["genres"]

    url = "https://open.spotify.com/track/" + song_id
    api_key = "49959aa679129bcf2cd919ba882b65d3"

    preview_url = f"http://api.linkpreview.net/?key={api_key}&q={url}"

    r = requests.get(preview_url)
    preview = r.json()


    return render_template('results.html', preview = preview, audioinfo = audioinfo, artist_name = artist_name, song_name=song_name)

    

if __name__ == '__main__':  
    app.run(debug=True)