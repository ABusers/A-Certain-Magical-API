# coding: utf-8
import json
import os
import sys
import urlparse
import webbrowser
import clipboard
import dialogs

# import the funimation file
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ROOT_PATH, '..'))
import funimation

f = funimation.Funimation()
def dumps(dictionary):
    return json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '))

config_file = '../config/ios-settings.json'
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            opener = json.load(f)['opener']
    except:
        with open(config_file, 'w') as f:
            f.write(dumps({'opener': 'Safari'}))
        opener = 'Safari'
else:
    with open(config_file, 'w') as f:
        f.write(dumps({'opener': 'Safari'}))
    opener = 'Safari'

url_scheme = {'Safari': 'safari-http://',
              'nPlayer': 'nplayer-http://',
              'Pythonista': 'http://',
              'Chrome': 'googlechrome://',
              'Clipboard': 'clipboard'}.get(opener, 'http://')

def showpicker():
    slist = [{'title': 'Opener'}]
    for i in f.get_shows():
        slist += [{'title': i.series_name, 'asset_id': i.asset_id}]
    return slist


def videos_list(item_list):
    vlist = []
    for parts in item_list:
        title = '{} : {}-{}'.format(parts.info['episode'], parts.title, parts.dub_sub)
        vlist += [{'title': title, 'url': parts.video_url}]
    return vlist


choice = dialogs.list_dialog('shows', showpicker())
if choice is None:
    sys.exit('Quit')
if choice['title'] is 'Opener':
    choice = dialogs.list_dialog('Open With', openwith)
    with open('ios-settings.json', 'w') as f:
        f.write(dumps({'opener': choice['title']}))
    sys.exit('Settings changed')
vtable = f.get_videos(choice['asset_id'])
videos = videos_list(vtable)
item = dialogs.list_dialog(choice['title'], videos)
if item is None:
    sys.exit('Quit')
url = urlparse.urlparse(item['url'])
if urlscheme is 'clipboard':
    clipboard.set(item['url'])
else:
    open_url = urlscheme + url.hostname + url.path + '?' + url.query
    webbrowser.open(open_url)
