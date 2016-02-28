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
# up a level to get to the funimation file
os.chdir('..')
import funimation as f


def dumps(dictionary):
    return json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '))


if os.path.exists('ios-settings.json'):
    try:
        config_ios = open('ios-settings.json', 'r')
        jsonstr = json.load(config_ios)
        opener = jsonstr['opener']
    except:
        config_ios = open('ios-settings.json', 'w')
        config_ios.write(dumps({'opener': 'Safari'}))
        config_ios.close()
        opener = 'Safari'
else:
    config = open('ios-settings.json', 'w')
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
        slist += [{'title': i.title, 'nid': i.nid, 'content_types': i.video_section}]
    return slist


def videos_list(item_list):
    vlist = []
    for parts in item_list:
        if type(parts) is f.Clip:
            item_url = f.stream_url(parts.funimation_id, parts.quality)
            vlist += [{'title': parts.title, 'url': item_url}]
        elif type(parts) is f.Movie:
            item_url = f.stream_url(parts.funimation_id, parts.quality)
            vlist += [{'title': parts.title + ' - ' + parts.sub_dub, 'url': item_url}]
        elif type(parts) is f.Episode:
            item_url = f.stream_url(parts.funimation_id, f.qual(parts))
            ep_num = str(parts.episode_number)
            vlist += [{'title': ep_num + ' : ' + parts.title + '-' + parts.sub_dub, 'url': item_url}]
        else:
            item_url = f.stream_url(parts.funimation_id, f.qual(parts))
            vlist += [{'title': parts.title, 'url': item_url}]
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
picked_type = dialogs.list_dialog('Type', choice['content_types'])
if picked_type is None:
    sys.exit('Quit')
vtable = f.get_videos(choice['nid'], picked_type)
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
