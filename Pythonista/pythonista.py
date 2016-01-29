# coding: utf-8
import dialogs
import os
import sys
import webbrowser
#import the funimation file
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ROOT_PATH, '..'))
#up a level to get to the funimation file
import funimation as f
import models as m


def showpicker():
    slist=[]
    n=0
    for i in f.get_shows():
        slist += [{'title': str(n)+': '+i.title,'nid': i.nid,'content_types': i.video_section}]
        n += 1
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
            item_url = f.stream_url(item.funimation_id, f.qual(item))
            vlist+=[{'title': i.title,'url': item_url}]
    return vlist

choice = dialogs.list_dialog('shows',showpicker())
if choice == None:
    sys.exit('Quit')

picked_type = dialogs.list_dialog('Type',choice['content_types'])
if picked_type == None:
    sys.exit('Quit')
vtable = f.get_videos(choice['nid'],picked_type)
videos = videos_list(vtable)
item = dialogs.list_dialog(choice['title'],videos)
if item == None:
    sys.exit('Quit')
webbrowser.open('safari-'+item['url'])