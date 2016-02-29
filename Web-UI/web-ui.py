#!/usr/bin/env python
# coding: utf-8

import os
import sys
from flask import Flask, render_template
# import the funimation file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import funimation as f

shows = f.get_shows()

app = Flask(__name__)
app.config.from_object('config')


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
    cdnurl = f.stream_url
    return render_template('episodes.html', eps=eps, title=title, cdnurl=cdnurl)


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
