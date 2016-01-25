import json
import os.path as path
import urllib
import urllib2
from datetime import datetime
from time import strptime

from models import *

def dumps(dict):
	json.dumps(dict,sort_keys=True,indent=4,separators=(',', ': '))


# sub and dub is 0=both 1=sub only 2=dub only

if path.exists('settings.json'):
    try:
        config = open('settings.json', 'r')
        settings = json.loads(config.read())
        sub_dub = settings['sub_dub']
    except:
        config = open('settings.json', 'w')
        config.write(dumps({'sub_dub': 0}))
        config.close()
        sub_dub = 0
else:
    config = open('settings.json', 'w')
    config.write(dumps({'sub_dub': 0}))
    config.close()
    sub_dub = 0

base_url = 'http://wpc.8c48.edgecastcdn.net'
bitrate = [2000, 3500, 4000]
funimation_url = 'https://www.funimation.com/'
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
    'stream': 'http://wpc.8c48.edgecastcdn.net/038C48/SV/480/{video_id}/{video_id}-480-{quality}K.mp4.m3u8?9b303b6c62204a9dcb5ce5f5c607',
}


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

    if data[0].has_key('group_title'):
        return [EpisodeDetail(**i) for i in data]
    elif data[0].has_key('maturity_rating'):
        return [Show(**i) for i in data]
    elif data[0].has_key('episode_number'):
        return [Episode(**i) for i in data]
    elif data[0].has_key('tv_key_art'):
        return [Movie(**i) for i in data]
    elif data[0].has_key('funimationid'):
        return [Clip(**i) for i in data]
    elif data[0].has_key('is_mature'):
        return [Trailer(**i) for i in data]
    else:
        return data


def filter_response(data):
    # just check the first object since all will be the same
    if data[0].get('sub_dub') is None:
        return data
    # both
    if sub_dub == 0:
        return data
    # sub
    elif sub_dub == 1:
        ret = [ep for ep in data if ep.sub]
        return ret
    # dub
    elif sub_dub == 2:
        ret = [ep for ep in data if ep.dub]
        return ret
    else:
        # just in case
        return data


def process_data(url):
    resp = get(url)
    data = process_response(resp)
    return filter_response(data)


def get_data_url(endpoint, series=0, pg=0):
    if endpoint == 'shows':
        params = check_params(sort='alpha')
        url = urls[endpoint].format(**params)
        return url
    if series != 0:
        params = check_params(showid=series,page=pg)
        url = urls[endpoint].format(**params)
        return url
    params = check_params()
    url = urls[endpoint].format(**params)
    return url


def check_params(showid=0, page=0, sort=None, order=None, limit=None, rating=None, genre=None, term=None):
    if sort is None or sort not in sort_types:
        sort = 'date'

    if order is None or order not in order_types:
        order = 'asc'

    if limit is None or not limit.isdigit():
        limit = 'nl'  # no limit

    if rating is None or rating not in rating_type:
        rating = 'all'

    if genre is None or genre not in genre_types:
        genre = 'all'

    if term is None:
        term = ''
    v_type = 'subscription'
    return locals()


def get(endpoint, params=None):
    if endpoint.startswith('http'):
        url = endpoint
    else:
        url = base_url.format(endpoint)
    if params is None:
        content = urllib2.urlopen(url).read()
    else:
        content = urllib2.urlopen(url + urllib.urlencode(params)).read()
    return json.loads(content)


def stream_url(video_id, quality):
    url = urls['stream'].format(**locals())
    return url


def qual(episode):
    q = len(episode.video_quality) - 1
    return bitrate[q]


def get_shows():
    show_url = get_data_url('shows')
    shows = process_data(funimation_url + show_url)
    return shows


# Strings episode pages together
def get_episodes(show_id):
    eplist = process_data(funimation_url+get_data_url('episodes',show_id))
    for pgs in range(1,30):
        url = funimation_url+get_data_url('episodes',show_id,pgs)
        returns = get(url)
        if returns:
            eplist += process_data(funimation_url + get_data_url('episodes', show_id, pgs))
        else:
            return eplist


def print_shows(show_list):
    for item in range(0, len(show_list)):
        title = show_list[item].title
        print item, ':', title, '- nid:', show_list[item].nid


def print_eps(ep_list):
    for item in range(0,len(ep_list)):
        title = ep_list[item].title
        ep_number = ep_list[item].episode_number
        lang = ep_list[item].sub_dub
        ep_url = stream_url(ep_list[item].funimation_id,qual(ep_list[item]))
        print ep_number,':',title,'-',lang,':',ep_url