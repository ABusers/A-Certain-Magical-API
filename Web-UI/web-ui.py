#!/usr/bin/env python
# coding: utf-8

import os
import sys
import requests
from flask import Flask, make_response, render_template
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
    return render_template('episodes.html', eps=eps, title=title, n=n, subdub=subdub, cdnurl=f.stream_url)


@app.route('/show/<int:n>/<subdub>/<int:episode_number>/<int:quality>/play', defaults={'filename': None})
@app.route('/show/<int:n>/<subdub>/<int:episode_number>/<int:quality>/play/<filename>')
def play_episode(n, subdub, episode_number, quality, filename):
    # Discard filename, that's just to make the browser happy.

    nid = shows[n].nid

    # Gross, needs architecture fix
    episode = None
    for ep in f.get_videos(int(nid)):
        if ep.sub_dub.lower() == subdub and ep.episode_number == episode_number:
            episode = ep
            break

    playlist_url = f.stream_url(episode.funimation_id, quality)  # , episode.quality)

    response = make_response("#EXTM3U\n"+playlist_url)
    response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
    if filename is not None:
        response.headers['Content-Disposition'] = 'attachment'
    else:
        response.headers['Content-Disposition'] = 'attachment; filename=stream.m3u8'
    return response


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
