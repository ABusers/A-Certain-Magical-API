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
        config_ios = open(config_file, 'r')
        jsonstr = json.load(config_ios)
        opener = jsonstr['opener']
    except:
        config_ios = open(config_file, 'w')
        config_ios.write(dumps({'opener': 'Safari'}))
        config_ios.close()
        opener = 'Safari'
else:
    config = open(config_file, 'w')
    config.write(dumps({'opener': 'Safari'}))
    config.close()
    opener = 'Safari'

openwith = [
    {'urlscheme': 'safari-http://', 'title': 'Safari'},
    {'urlscheme': 'nplayer-http://', 'title': 'nPlayer'},
    {'urlscheme': 'http://', 'title': 'Pythonista'},
    {'urlscheme': 'googlechrome://', 'title': 'Chrome'},
    {'urlscheme': 'clipboard', 'title': 'Clipboard'}]

for i in openwith:
    if opener == i['title']:
        urlscheme = i['urlscheme']
        break


def showpicker():
    slist = [{'title': 'Opener'}]
    for i in f.get_shows():
        slist += [{'title': i.series_name, 'asset_id': i.asset_id, 'content_types': i.video_section}]
    return slist


def videos_list(item_list):
    vlist = []
    for parts in item_list:
        item_url = parts.video_url
        ep_num = str(parts.info['episode'])
        vlist += [{'title': ep_num + ' : ' + parts.title + '-' + parts.dub_sub, 'url': item_url}]
    return vlist


choice = dialogs.list_dialog('shows', showpicker())
if choice is None:
    sys.exit('Quit')
if choice['title'] is 'Opener':
    choice = dialogs.list_dialog('Open With', openwith)
    config_ios = open('ios-settings.json', 'w')
    config_ios.write(dumps({'opener': choice['title']}))
    config_ios.close()
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
