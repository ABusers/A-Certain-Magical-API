# -*- coding: utf-8 -*-
import os
import json
import requests
import datetime
import requests_cache
expire_after = datetime.timedelta(days=1)
cache = requests_cache.core.install_cache('../cache',expire_after=expire_after)
__all__ = ['HTTPClient']


class HTTPClient(object):

    def __init__(self, base_url='', headers=None):
        super(HTTPClient, self).__init__()
        self.base_url = base_url

    def get(self, url, query=None):
        return self._request(self._build_request(url, params=query))

    def post(self, url, data):
        return self._request(self._build_request(url, data))

    def _request(self, request):
        content = request.json()
        return content

    def _build_request(self, url, data=None, params=None):
        if not url.startswith('http'):
            url = self.base_url + url
        if data is not None:
            if isinstance(data, dict):
                req = requests.get(url, json=data,
                                      headers={'Content-Type': 'application/json'})
            else:
                req = requests.get(url, payload=data)
        else:
            req = requests.get(url,params=params)
        return req