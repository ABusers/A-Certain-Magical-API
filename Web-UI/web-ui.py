#!/usr/bin/env python
# coding: utf-8

import os
import sys
import requests
from flask import Flask, Response, render_template
# import the funimation file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import funimation as f

app = Flask(__name__)
app.config.from_object('config')

shows = f.get_shows()

s = requests.session()
s.headers = {'User-Agent: FAPI Web'}


@app.route('/')
def index():
    return render_template('shows.html', shows=shows)


@app.route('/show/<int:n>/<subdub>')
def show(n, subdub):
    if subdub not in ["sub", "dub"]:
        return "Error: invalid sub/dub selection"
    nid = shows[n].nid
    eps = [x for x in f.get_videos(int(nid)) if x.sub_dub.lower() == subdub]  # Hacky, needs architecture fix
    title = shows[n].label
    return render_template('episodes.html', eps=eps, title=title, n=n, subdub=subdub)


@app.route('/show/<int:n>/<subdub>/<int:episode_number>/<int:quality>/play')
def play_episode(n, subdub, episode_number, quality):
    nid = shows[n].nid

    # Gross, needs architecture fix
    episode = None
    for ep in f.get_videos(int(nid)):
        if ep.sub_dub.lower() == subdub and ep.episode_number == episode_number:
            episode = ep
            break

    playlist_url = f.stream_url(episode.funimation_id, quality)  # , episode.quality)

    rebuilt_playlist = "#EXTM3U\n"+playlist_url
    return Response(rebuilt_playlist, mimetype="application/vnd.apple.mpegurl")


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
