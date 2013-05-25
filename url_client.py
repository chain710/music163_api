#!/usr/bin/env python
#coding=utf-8

#url client

from demjson import decode as decode_json
import urllib
import urllib2
import logging
import cookielib

# u = url_client('http://api.douban.com')
# print u.movie__subject__imdb__json(extra_uri=['tt0213338'],params={'alt':'json', 'apikey':'123'})

class url_client(object):
    support_data_type = ['json']
    cookies = cookielib.CookieJar()
    def __init__(self, base_url, def_params = {}):
        self.base_url = base_url
        self.def_params = def_params
    def get_cookies(self):
        return self.cookies
    def __getattr__(self, name):
        name_parts = name.split('__')
        dt = name_parts[-1].lower()
        if dt in self.support_data_type:
            name_parts.pop()
        else:
            dt = None
        apiurl = '%s/%s'%(self.base_url, '/'.join(name_parts))
        def wrap(**kw):
            extra = kw.get('extra_uri', [])
            url = apiurl if len(extra)==0 else '%s/%s'%(apiurl, '/'.join(map(str, extra)))
            params = kw.get('params', {})
            params.update(self.def_params)
            return self.__call__(url = url,
                params = params,
                payload = kw.get('payload', ''), 
                method = kw.get('method', 'GET'), 
                headers = kw.get('headers', {}), 
                data_type = dt)
        return wrap
        
    def __call__(self, url, params, payload, method, headers, data_type):
        try:
            if len(params) > 0:
                url += '?' + urllib.urlencode(params)
                
            if ('GET' == method.upper()):
                body = None
            else:
                if (None != payload):
                    body = payload if isinstance(payload, str) else urllib.urlencode(payload)
                else:
                    body = ''
                    
            logging.debug("http url=%s"%(url))
            request = urllib2.Request(url, body, headers)
            content = ''
            try:
                response = urllib2.urlopen(request, timeout=3)
                content = response.read()
                self.cookies.extract_cookies(response, request)
            except urllib2.HttpError, e:
                logging.error("http error: %d", e.code)
            except urllib2.URLError, e:
                logging.error("url error!")
            
            logging.debug("http response: %s"%content)
            # TODO: support xml .etc
            if data_type == 'json':
                return decode_json(content)
            else:
                return content
        except Exception as e:
            logging.error('url(%s) encounter unexpected err %s!'%(url, e))
            return None
            