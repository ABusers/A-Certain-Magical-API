# coding: utf-8
import dialogs
import os
import sys
import webbrowser
import urlparse
import json
#import the funimation file
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ROOT_PATH, '..'))
#up a level to get to the funimation file
import funimation as f
import models as m



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
    
openwith=[
{'urlscheme': 'safari-http://','title': 'Safari'},
{'urlscheme': 'nplayer-http://','title': 'nPlayer'},
{'urlscheme': 'http://','title': 'Pythonista'},
{'urlscheme': 'googlechrome://','title': 'Chrome'}]

os.chdir('..')

for i in openwith:
    if opener == i['title']:
        urlscheme = i['urlscheme']
        break

def showpicker():
    slist=[{'title':'Settings'}]
    for i in f.get_shows():
        slist += [{'title': i.title,'nid': i.nid,'content_types': i.video_section}]
    return slist


def videos_list(item_list):
    vlist=[]
    for i in item_list:
        if type(i) == m.Clip:
            item_url = f.stream_url(i.funimation_id, i.quality)
            vlist+=[{'title': i.title,'url': item_url}]
        elif type(i) == m.Movie:
            item_url = f.stream_url(i.funimation_id, i.quality)
            vlist+=[{'title': i.title+' - '+i.sub_dub,'url': item_url}]
        elif type(i) == m.Episode:
            item_url = f.stream_url(i.funimation_id, f.qual(i))
            ep_num = str(i.episode_number)
            vlist += [{'title': ep_num+' : '+i.title+'-'+i.sub_dub,'url': item_url}]
        else:
            item_url = f.stream_url(i.funimation_id, f.qual(i))
            vlist+=[{'title': i.title,'url': item_url}]
    return vlist



choice = dialogs.list_dialog('shows',showpicker())
if choice == None:
    sys.exit('Quit')
if choice['title'] == 'Settings':
    choice = dialogs.list_dialog('Open With',openwith)
    config_ios = open('ios-settings.json', 'w')
    config_ios.write(dumps({'opener': choice['title']}))
    config_ios.close()
    sys.exit('Settings changed')
picked_type = dialogs.list_dialog('Type',choice['content_types'])
if picked_type == None:
    sys.exit('Quit')
vtable = f.get_videos(choice['nid'],picked_type)
videos = videos_list(vtable)
item = dialogs.list_dialog(choice['title'],videos)
if item == None:
    sys.exit('Quit')
url = urlparse.urlparse(item['url'])
open_url=urlscheme+url.hostname+url.path+'?'+url.query
webbrowser.open(open_url)