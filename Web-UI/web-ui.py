# coding: utf-8
import os
import sys
import json
from flask import Flask, render_template
# import the funimation file
ROOT_PATH = os.getcwd()
sys.path.append(os.path.join(ROOT_PATH, '..'))
import funimation as f


def dumps(dictionary):
    return json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '))

config_file = '../config/web-ui.json'
if os.path.exists(config_file):
    try:
        config = open(config_file, 'r')
        jsonstr = json.load(config)
        debug = jsonstr['Debug']
        port = jsonstr['Port']
        public = jsonstr['Public']
    except:
        config = open(config_file, 'w')
        config.write(dumps({'Debug': True, 'Port': 8080, 'Public': False}))
        config.close()
        debug = True
        port = 8080
        public = False

else:
    config = open(config_file, 'w')
    config.write(dumps({'Debug': True, 'Port': 8080, 'Public': False}))
    config.close()
    debug = True
    port = 8080
    public = False

if public:
    bind = '0.0.0.0'
else:
    bind = '127.0.0.1'
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
    app.run(port=port,debug=debug,host=bind)
    print 'done'
