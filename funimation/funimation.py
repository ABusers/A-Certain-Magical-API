"""
Funimation API
~~~~~~~~~~~~~~

This file implements tools for working with the
Funimation video streaming service.

:copyright: (c) 2015 ABusers
:license: MIT See LICENSE for details

"""

import json
import os
import requests
from datetime import datetime
from time import strptime
from models import *
import time


def dumps(dictionary):
    return json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '))


class Settings:
    """
    This class holds the variables for settings.
    """
    sub_dub = 'both'
    caching = False
    json = str
    timeout = 15.0


class Api:
    """
    This class holds static variables to make writing
    new code easier.
    """
    cdn_url = 'http://wpc.8c48.edgecastcdn.net'
    bit_rate = [2000, 3500, 4000]
    api_url = 'https://www.funimation.com/'
    order_types = ['asc', 'desc']
    rating_type = ['tvpg', 'tv14', 'tvma', 'nr', 'pg', 'pg13', 'r', 'all']
    sort_types = ['alpha', 'date', 'dvd', 'now', 'soon', 'votes', 'episode',
                  'title', 'sequence']
    genre_types = ['all', 'action', 'adventure', 'bishonen', 'bishoujo', 'comedy',
                   'cyberpunk', 'drama', 'fan service', 'fantasy', 'harem',
                   'historical', 'horror', 'live action', 'magical girl',
                   'martial arts', 'mecha', 'moe', 'mystery', 'reverse harem',
                   'romance', 'school', 'sci fi', 'shonen', 'slice of life',
                   'space', 'sports', 'super power', 'supernatural', 'yuri']
    urls = {
        'details': 'mobile/node/{showid}',
        'search': 'mobile/shows.json/alpha/asc/nl/all/all?keys={term}',
        'shows': 'mobile/shows.json/{sort}/{order}/{limit}/{rating}/{genre}',
        'clips': 'mobile/clips.json/sequence/{order}/{showid}/all/all?page={page}',
        'trailers': 'mobile/trailers.json/sequence/{order}/{showid}/all/all?page={page}',
        'movies': 'mobile/movies.json/{v_type}/{sort}/{order}/all/{showid}?page={page}',
        'episodes': 'mobile/episodes.json/{v_type}/sequence/{order}/all/{showid}?page={page}',
        'stream': ('http://wpc.8c48.edgecastcdn.net/038C48/SV/480/'
                   '{video_id}/{video_id}-480-{quality}K.mp4.m3u8?9b303b6c62204a9dcb5ce5f5c607'),
    }

'''
Attempting to make sure that all the config and cache goes into one directory
'''
config_path = '.'
config_dir = '/config/'
config_file = 'settings.json'
if not os.path.exists('config/'):
    config_path = '..'
    if not os.path.exists(config_path+config_dir):
        os.mkdir(config_path+config_dir)
resolved_settings = config_path+config_dir+config_file
cache_dir = config_path+config_dir+'/cache/'
if os.path.exists(resolved_settings):
    try:
        config = open(resolved_settings, 'r')
        Settings.json = json.loads(config.read())
        Settings.sub_dub = Settings.json['sub_dub']
        Settings.caching = Settings.json['caching']
        Settings.timeout = float(Settings.json['timeout'])
    except:
        config = open(resolved_settings, 'w')
        config.write(dumps({'sub_dub': 'both', 'caching': False, 'timeout': 15.0}))
        config.close()
        Settings.sub_dub = 'both'
        Settings.caching = False
        Settings.timeout = 15.0
else:
    config = open(resolved_settings, 'w')
    config.write(dumps({'sub_dub': 'both', 'caching': False, 'timeout': 15.0}))
    config.close()
    Settings.sub_dub = 'both'
    Settings.caching = False
    Settings.timeout = 15.0


def fix_keys(d):
    def fix_key(key):
        return key.lower().replace(' ', '_').replace('-', '_')

    def fix(x):
        if isinstance(x, dict):
            return dict((fix_key(k), fix(v)) for k, v in x.iteritems())
        elif isinstance(x, list):
            return [fix(i) for i in x]
        else:
            return x

    return fix(d)


def convert_values(d):
    for k, v in d.items():
        if k == 'video_section' or k == 'aip':
            d[k] = v.values() if isinstance(v, dict) else []
        elif k == 'votes' or k == 'nid' or k == 'show_id':
            d[k] = int(v) if v is not None else 0
        elif k == 'episode_number':
            d[k] = int(float(v)) if v is not None else 0
        elif k == 'post_date':
            try:
                d[k] = datetime.strptime(v, '%m/%d/%Y')
            except TypeError:
                d[k] = datetime(*(strptime(v, '%m/%d/%Y')[0:6]))
        elif k == 'duration':
            d[k] = v
        elif k == 'all_terms' or k == 'term':
            d[k] = v.split(', ')
        elif k == 'similar_shows':
            d[k] = [int(i) for i in v.split(',') if isinstance(i, list)]
        elif k == 'video_quality':
            d[k] = v.values() if isinstance(v, dict) else [d[k]]
        elif k == 'promo':
            d[k] = v == 'Promo'
        elif k == 'type':
            d[k] = v[7:]
        elif k == 'maturity_rating':
            d[k] = str(v)
        elif k == 'mpaa':
            d[k] = ','.join(v.values()) if isinstance(v, dict) else v

    return d


def process_response(data):
    # collapse data into list of dicts
    data = [i[i.keys()[0]] for i in data[data.keys()[0]]]
    # fix dict key names
    data = fix_keys(data)
    # fix up the values
    data = [convert_values(i) for i in data]

    if 'group_title' in data[0]:
        return [EpisodeDetail(**i) for i in data]
    elif 'maturity_rating' in data[0]:
        return [Show(**i) for i in data]
    elif 'episode_number' in data[0]:
        return [Episode(**i) for i in data]
    elif 'tv_key_art' in data[0]:
        return [Movie(**i) for i in data]
    elif 'funimationid' in data[0]:
        return [Clip(**i) for i in data]
    elif 'is_mature' in data[0]:
        return [Trailer(**i) for i in data]
    else:
        return data


def filter_response(data):
    if data[0].get('sub_dub') is None:
        return data
    # both
    if Settings.sub_dub == 'both':
        return data
    # sub
    elif Settings.sub_dub == 'sub':
        ret = [ep for ep in data if ep.sub]
        return ret
    # dub
    elif Settings.sub_dub == 'dub':
        ret = [ep for ep in data if ep.dub]
        return ret
    else:
        # just in case
        return data


def process_data(url):
    resp = try_cache(url)
    data = process_response(resp)
    return filter_response(data)


def get_data_url(endpoint, series=0, pg=0):
    if endpoint == 'shows':
        params = check_params(sort='alpha')
        url = Api.urls[endpoint].format(**params)
        return url
    if series != 0:
        params = check_params(showid=series, page=pg)
        url = Api.urls[endpoint].format(**params)
        return url
    params = check_params()
    url = Api.urls[endpoint].format(**params)
    return url


def check_params(showid=0, page=0, sort=None, order=None, limit=None, rating=None, genre=None, term=None):
    if sort is None or sort not in Api.sort_types:
        sort = 'date'

    if order is None or order not in Api.order_types:
        order = 'asc'

    if limit is None or not limit.isdigit():
        limit = 'nl'  # no limit

    if rating is None or rating not in Api.rating_type:
        rating = 'all'

    if genre is None or genre not in Api.genre_types:
        genre = 'all'

    if term is None:
        term = ''
    v_type = 'subscription'
    return locals()


def get(endpoint, params=None):
    if endpoint.startswith('http'):
        url = endpoint
    else:
        url = Api.cdn_url.format(endpoint)
    if params is None:
        content = requests.get(url, timeout=Settings.timeout)
    else:
        content = requests.get(url, params=params, timeout=Settings.timeout)
    if Settings.caching:
        cache_file = url.replace(Api.api_url, '')
        cache_file = cache_dir + cache_file.replace('/', '`') + '.json'
        cache = open(cache_file, 'w')
        cache.write(content.text)
        cache.close()
    return content.json()


def try_cache(url):
    if Settings.caching:
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        cache_file = url.replace(Api.api_url, '')
        cache_file = cache_dir + cache_file.replace('/', '`') + '.json'
        if os.path.exists(cache_file):
            last_modified = os.path.getmtime(cache_file)
            if (time.time() - last_modified) / 86400 < 1:
                try:
                    data = json.loads(open(cache_file).read())
                    print 'got from cache'
                    return data
                except:
                    return get(url)
            else:
                return get(url)
        else:
            return get(url)
    else:
        return get(url)


def stream_url(video_id, quality):
    url = Api.urls['stream'].format(**locals())
    return url


def qual(episode):
    q = len(episode.video_quality) - 1
    return Api.bit_rate[q]


def get_shows():
    show_url = get_data_url('shows')
    shows = process_data(Api.api_url + show_url)
    # Changing the mobile image urls to Xbox images
    for k in range(0,len(shows)):
        shows[k].show_thumbnail = shows[k].show_thumbnail.replace('1_thumbnail','xbox_thumbnail')
        shows[k].show_thumbnail_accedo = shows[k].show_thumbnail_accedo.replace('1_thumbnail','xbox_thumbnail')
    return shows


def get_videos(show_id, item_type='Episodes'):
    if item_type in ['Episodes', 'episodes', 'e']:
        item_list = process_data(Api.api_url + get_data_url('episodes', show_id))
        for pgs in range(1, 30):
            url = Api.api_url + get_data_url('episodes', show_id, pgs)
            returns = get(url)
            if returns:
                item_list += process_data(Api.api_url + get_data_url('episodes', show_id, pgs))
            else:
                return item_list
    elif item_type in ['Clips', 'clips', 'c']:
        item_list = process_data(Api.api_url + get_data_url('clips', show_id))
        for pgs in range(1, 30):
            url = Api.api_url + get_data_url('clips', show_id, pgs)
            returns = get(url)
            if returns:
                item_list += process_data(Api.api_url + get_data_url('clips', show_id, pgs))
            else:
                return item_list
    elif item_type in ['Movies', 'movies', 'm']:
        item_list = process_data(Api.api_url + get_data_url('movies', show_id))
        for pgs in range(1, 30):
            url = Api.api_url + get_data_url('movies', show_id, pgs)
            returns = get(url)
            if returns:
                item_list += process_data(Api.api_url + get_data_url('movies', show_id, pgs))
            else:
                return item_list
    elif item_type in ['Trailers', 'trailers', 't']:
        item_list = process_data(Api.api_url + get_data_url('trailers', show_id))
        for pgs in range(1, 30):
            url = Api.api_url + get_data_url('trailers', show_id, pgs)
            returns = get(url)
            if returns:
                item_list += process_data(Api.api_url + get_data_url('trailers', show_id, pgs))
            else:
                return item_list


def print_shows(show_list):
    n = 0
    for item in show_list:
        title = item.title
        print n, ':', title, '- nid:', item.nid
        n += 1


def print_videos(item_list):
    for item in item_list:
        if type(item) == Clip:
            title = item.title
            item_url = stream_url(item.funimation_id, item.quality)
            print title, ':', item_url
        elif type(item) == Movie:
            title = item.title
            item_url = stream_url(item.funimation_id, item.quality)
            print title, '-', item.sub_dub, ':', item_url
        elif type(item) == Episode:
            title = item.title
            ep_number = item.episode_number
            lang = item.sub_dub
            item_url = stream_url(item.funimation_id, qual(item))
            print ep_number, ':', title, '-', lang, ':', item_url
        else:
            title = item.title
            item_url = stream_url(item.funimation_id, qual(item))
            print title, ':', item_url


def set_settings(sub_dub='both', caching=False, timeout=15.0):
    if sub_dub not in {'both', 'sub', 'dub'}:
        print 'Invalid sub/dub setting'
        return
    if type(caching) != bool:
        print 'Invalid caching setting'
        return
    if type(timeout) != float:
        print 'Invalid timeout setting'
        return
    set_conf = open('settings.json', 'w')
    set_conf.write(dumps({'sub_dub': sub_dub, 'caching': caching, 'timeout': timeout}))
    set_conf.close()
    Settings.sub_dub = sub_dub
    Settings.caching = caching
