# -*- coding: utf-8 -*-
import os
import json
import urllib2
import requests
import datetime
import requests_cache
from urllib import urlencode

expire_after = datetime.timedelta(days=1)
cache = requests_cache.core.install_cache('cache',expire_after=expire_after)
__all__ = ['HTTPClient']


class HTTPClient(object):

    def __init__(self, base_url='', headers=None):
        super(HTTPClient, self).__init__()
        self.base_url = base_url

    def get(self, url, query=None):
        if query is not None:
            if isinstance(query, dict):
                q = dict((k, v) for k, v in query.iteritems() if v is not None)
                url = url + '?' + urlencode(q)
            else:
                url = url + '?' + query
        return self._request(self._build_request(url))

    def post(self, url, data):
        return self._request(self._build_request(url, data))

    def _request(self, request):
        content = request.json()
        return content

    def _build_request(self, url, data=None):
        if not url.startswith('http'):
            url = self.base_url + url
        if data is not None:
            if isinstance(data, dict):
                req = urllib2.Request(url, json.dumps(data),
                                      headers={'Content-Type': 'application/json'})
            else:
                req = urllib2.Request(url, data)
        else:
            req = requests.get(url)
        return req
