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
s.headers = {'User-Agent: FAPI Web'}


@app.context_processor
def set_version():
    return {'version': version}


@app.route('/')
def index():
    return render_template('shows.html', shows=shows)


@app.route('/show/<int:n>/<subdub>')
def show(n, subdub):
    if subdub not in ["sub", "dub"]:
        return "Error: invalid sub/dub selection"
    show_id = shows[n].asset_id
    try:
        eps = [x for x in f.get_videos(int(show_id)) if x.dub_sub.lower() == subdub]  # Hacky, needs architecture fix
    except AttributeError:  # FIXME: This is not the correct way to do this.
        return render_template('message.html', message="API Error: Does this show have any episodes?")
    title = shows[n].label
    return render_template('episodes.html', eps=eps, title=title, n=n, subdub=subdub)


@app.route('/show/<int:n>/<subdub>/<int:episode_number>/play', defaults={'filename': None})
@app.route('/show/<int:n>/<subdub>/<int:episode_number>/play/<filename>')
def play_episode(n, subdub, episode_number, filename):
    # Discard filename, that's just to make the browser happy.

    asset_id = shows[n].asset_id

    # Gross, needs architecture fix
    episode = None
    for ep in f.get_videos(int(asset_id)):
        if ep.sub_dub.lower() == subdub and ep.episode_number == episode_number:
            episode = ep
            break

    playlist_url = episode.video_url # , episode.quality)

    response = make_response("#EXTM3U\n"+playlist_url)
    response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
    if filename is not None:
        response.headers['Content-Disposition'] = 'attachment'
    else:
        response.headers['Content-Disposition'] = 'attachment; filename=stream.m3u8'
    return response


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
