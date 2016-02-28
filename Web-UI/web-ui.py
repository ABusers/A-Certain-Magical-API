# coding: utf-8
import os
import sys
from flask import Flask, render_template
# import the funimation file
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ROOT_PATH, '..'))
# up a level to get to the funimation file
os.chdir('..')
import funimation as f

debug = True

shows = f.get_shows()
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('shows.html', shows=shows, len=len)


@app.route('/show/<n>')
def show(n):
    n = int(n)
    nid = shows[n].nid
    eps = f.get_videos(int(nid))
    title = shows[n].label
    cdnurl = f.stream_url
    return render_template('eps.html', eps=eps, len=len,title=title,cdnurl=cdnurl)


if __name__ == '__main__':
    app.run(port=80,debug=debug)
    print 'done'
