#!/usr/bin/env python
# coding: utf-8
import os
import sys
import requests
from flask import Flask, make_response, render_template
# import the funimation file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import funimation
from subprocess import check_output

f = funimation.Funimation()
if sys.platform not in {'iphoneos', 'win32'}:
    version = check_output(['git', 'rev-parse', '--short', 'HEAD'])
else:
    version = 'Unavailable'

app = Flask(__name__)
app.config.from_object('config')

shows = f.get_shows()

s = requests.session()
s.headers = {'User-Agent': 'Sony-PS3'}


@app.context_processor
def set_version():
    return {'version': version}


@app.route('/')
def index():
    return render_template('shows.html', shows=shows)


@app.route('/show/<int:asset_id>/<subdub>')
def show(asset_id, subdub):
    show_title = shows[shows.index(str(asset_id))].label
    if subdub not in ["sub", "dub"]:
        return "Error: invalid sub/dub selection"
    try:
        eps = [x for x in f.get_videos(int(asset_id)) if x.dub_sub.lower() == subdub]  # Hacky, needs architecture fix
    except AttributeError:  # FIXME: This is not the correct way to do this.
        return render_template('message.html', message="API Error: Does this show have any episodes?")
    return render_template('episodes.html', title=show_title, eps=eps, show_id=asset_id, subdub=subdub)


@app.route('/show/<int:asset_id>/<int:episode_id>/play', defaults={'filename': None})
@app.route('/show/<int:asset_id>/<int:episode_id>/play/<filename>')
def play_episode(asset_id, episode_id, filename):
    # Discard filename, that's just to make the browser happy.

    # Gross, needs architecture fix
    episode = None
    for ep in f.get_videos(asset_id):
        if int(ep.asset_id) == episode_id:
            episode = ep
            break

    playlist_url = episode.video_url

    response = make_response("#EXTM3U\n"+playlist_url)
    response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
    if filename is not None:
        response.headers['Content-Disposition'] = 'attachment'
    else:
        response.headers['Content-Disposition'] = 'attachment; filename=stream.m3u8'
    return response


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
