from url_client import url_client
import hashlib
import logging

import os
import urllib2

class music163_api(object):
    SEARCH_SONG = 1
    SEARCH_ARTIST = 100
    SEARCH_ALBUM = 10
    SEARCH_PLAYLIST = 1000
    SEARCH_USER = 1002
    
    cookies_ = ""
    def __init__(self):
        self.cli_ = url_client("http://music.163.com")
        
    def login(self, user, pwd):
        d = self.cli_.api__login__json(method='POST', payload={'password': hashlib.md5(pwd).hexdigest(), 'username':user})
        self.cookies_ = ';'.join(["%s=%s"%(c.name,c.value) for c in self.cli_.get_cookies()])
        return d
        
    def search(self, kw, type, limit, offset):
        payload = {'limit': limit, 'sub': 'false', 's': kw, 'type': type, 'offset': offset}
        return self.cli_.api__search__get__json(method='POST', payload=payload, headers = {'Cookie':self.cookies_})
        
    def song_detail(self, ids):
        payload = {'ids': '[%s]'%(','.join(map(str, ids)))}
        return self.cli_.api__song__detail__json(method='POST', payload=payload, headers = {'Cookie':self.cookies_})
        
    def album_detail(self, id):
        return self.cli_.api__album__json(method='GET', extra_uri=[id], headers = {'Cookie':self.cookies_})
        
    def artist_detail(self, id):
        #http://music.163.com/api/artist/20289?top=50(top hotest songs)
        return self.cli_.api__artist__json(method='GET', extra_uri=[id], headers = {'Cookie':self.cookies_})
        
    def artist_albums(self, id, offset, limit):
        #http://music.163.com/api/artist/albums/5770?offset=0&limit=20
        return self.cli_.api__artist__albums__json(method='GET', extra_uri=[id], params = {"offset":offset, "limit":limit}, headers = {'Cookie':self.cookies_})

def download_file(remote, local):
    f = urllib2.urlopen(remote)
    with open(local, "wb") as file:
        file.write(f.read())

def download_album(api, id, dst_dir):
    result = api.album_detail(id)
    #album/1-songname.mp3
    if result['code'] != 200:
        logging.error("invalid response code %d"%(result['code']))
        return
    
    album = result['album']
    dirname = '%s-%s'%(album['artist']['name'], album['name'])
    try:
        os.makedirs(os.sep.join([dst_dir, dirname]))
    except OSError, e:
        logging.error("create album failed, error %s"%(e))
        return
    
    if not album.has_key('songs'):
        logging.error("this album does not contain any songs!")
        return
    song_num = len(album['songs'])
    down_seq = 0
    for s in album['songs']:
        down_seq += 1
        song_file = "%d-%s.mp3"%(s['position'], s['name'])
        logging.debug("downloading [%d/%d] from %s", down_seq, song_num, s['mp3Url'])
        download_file(s['mp3Url'], os.sep.join([dirname, song_file]))
        
def list_album_of_artist(api, id):    
    more = True
    limit = 20
    offset = 0
    while more:
        result = api.artist_albums(id, offset, limit)
        offset += limit
        if result['code'] != 200:
            logging.error("invalid response code %d"%(result['code']))
            return
        albums = result['hotAlbums']
        more = result['more']
        for a in albums:
            print "%d-%s"%(a['id'],a['name'])

def search_artist(api, kw):
    result = api.search(kw, music163_api.SEARCH_ARTIST, 20, 0)
    if result['code'] != 200:
        logging.error("invalid response code %d"%(result['code']))
        return
        
    search = result['result']
    for a in search['artists']:
        print "%d-%s"%(a['id'],a['name'])
    
    #print id-artistname
logging.basicConfig(format='%(asctime)s|%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
api = music163_api()
#api.login('user', 'password')
download_album(api, 79766, ".")
#list_album_of_artist(api, 21131)
#search_artist(api, 'Rin')
#list_album_of_artist(api, 88148)

#api.search_song('love', 1002, 1, 0)
#print api.song_detail([167737,387948])

#print api.album_detail(279524)
#get_song_url('love', 2)
    