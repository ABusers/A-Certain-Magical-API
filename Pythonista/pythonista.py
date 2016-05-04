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
        with open(config_file, 'r') as in_file:
            opener = json.load(in_file)['opener']
    except:
        with open(config_file, 'w') as out_file:
            out_file.write(dumps({'opener': 'Safari'}))
        opener = 'Safari'
else:
    with open(config_file, 'w') as out_file:
        out_file.write(dumps({'opener': 'Safari'}))
    opener = 'Safari'

url_dict = {'Safari': 'safari-http://',
            'nPlayer': 'nplayer-http://',
            'Pythonista': 'http://',
            'Chrome': 'googlechrome://',
            'Clipboard': 'clipboard'}
url_scheme = url_dict.get(opener, 'http://')
openwith = [{'urlscheme': value, 'title': key} for key, value in url_dict.items()]


def showpicker():
    return [{'title': 'Opener'}] + [{'title': show.series_name,
             'asset_id': show.asset_id} for show in f.get_shows()]


def videos_list(item_list):
    return [{'title': '{} : {}-{}'.format(parts.info['episode'], parts.title,
              parts.dub_sub), 'url': parts.video_url} for parts in item_list]


choice = dialogs.list_dialog('shows', showpicker()) or sys.exit('Quit')
if choice['title'] is 'Opener':
    choice = dialogs.list_dialog('Open With', openwith)
    with open('ios-settings.json', 'w') as out_file:
        out_file.write(dumps({'opener': choice['title']}))
    sys.exit('Settings changed')
vtable = f.get_videos(choice['asset_id'])
videos = videos_list(vtable)
item = dialogs.list_dialog(choice['title'], videos) or sys.exit('Quit')
url = urlparse.urlparse(item['url'])
if urlscheme is 'clipboard':
    clipboard.set(item['url'])
else:
    open_url = urlscheme + url.hostname + url.path + '?' + url.query
    webbrowser.open(open_url)
