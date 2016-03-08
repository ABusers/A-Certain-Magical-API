# -*- coding: utf-8 -*-
from .httpclient import HTTPClient
from .models import Video, Show


__all__ = ['Funimation']


class Funimation(object):

    def __init__(self):
        super(Funimation, self).__init__()
        self.http = HTTPClient('http://www.funimation.com/',
                               [('User-Agent', 'Sony-PS3')])
        # defaults to the free account user
        # hmm... the API doesn't appear to validate the users subscription
        # level so if this was changed you might be able to watch
        # the paid videos ;)
        # FunimationSubscriptionUser = paid account
        # FunimationUser = free account
        self.user_type = 'FunimationSubscriptionUser'

    def get_shows(self, limit=3000, offset=0, sort=None, first_letter=None,
                  filter=None):
        query = self._build_query(locals())
        return self._request('feeds/ps/shows', query)

    def get_videos(self, show_id, limit=3000, offset=0):
        query = self._build_query(locals())
        request = self._request('feeds/ps/videos', query)
        for req in request:
            # Replace get params with the mobile one
            # This lets any IP (not only server IP) access content
            req.video_url = req.video_url.split('?')[0]+'?9b303b6c62204a9dcb5ce5f5c607'
            video_split = req.video_url.split(',')
            split_len = len(video_split)
            req.video_url = video_split[0]+video_split[split_len-2]+video_split[split_len-1]
        return request

    def get_featured(self, limit=3000, offset=0):
        query = self._build_query(locals())
        return self._request('feeds/ps/featured', query)

    def search(self, search):
        query = self._build_query(locals())
        return self._request('feeds/ps/search', query)

    def get_latest(self, limit=3000, offset=0):
        if self.user_type == 'FunimationSubscriptionUser':
            sort = 'SortOptionLatestSubscription'
        else:
            sort = 'SortOptionLatestFree'
        return self.get_shows(limit, offset, sort)

    def get_simulcast(self, limit=3000, offset=0):
        return self.get_shows(limit, offset, filter='FilterOptionSimulcast')

    def get_genres(self):
        # we have to loop over all the shows to be sure to get all the genres.
        # use a 'set' so duplicates are ignored.
        genres = set()
        for show in self.get_shows():
            if show.get('genres'):
                [genres.add(g) for g in show.get('genres').split(',')]
        return sorted(genres)

    def get_shows_by_genre(self, genre):
        shows = []
        for show in self.get_shows():
            if show.get('genres') and genre in show.get('genres').split(','):
                shows.append(show)
        return shows


    def _request(self, uri, query):
        res = self.http.get(uri, query)
        if 'videos' in res:
            return [Video(**v) for v in res['videos']]
        elif isinstance(res, list) and 'series_name' in res[0]:
            return [Show(**s) for s in res]
        else:
            # search results
            new_res = {}
            # the result is a list when there is no episodes in the results...
            if isinstance(res['episodes'], list):
                new_res['episodes'] = []
            else:
                new_res['episodes'] = [Video(**v) for v in
                                       res['episodes']['videos']]
            new_res['shows'] = [Show(**s) for s in res['shows']]
            return new_res

    def _build_query(self, params):
        if params is None:
            params = {}
        else:
            params['first-letter'] = params.pop('first_letter', None)
        params.pop('self', None)
        params.setdefault('ut', self.user_type)
        return params