import os
import xbmc
import xbmcgui
import xbmcaddon
import simplecache
import datetime
import json

from urllib2 import Request 
from urllib2 import urlopen
from random import choice
from resources.lib.movie_genres import movie_genres
from resources.lib.tv_genres import tv_genres


addon = xbmcaddon.Addon('sscript.screensaver.moviesandtvshows')
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')


monitor = xbmc.Monitor()
timer = [10,15,20,30,45,60][int(addon.getSetting("RotateTime"))]
date = (datetime.datetime.utcnow() - datetime.timedelta(hours = 12))
today = (date).strftime('%Y-%m-%d')


api_key = '?api_key=d41fd9978486321b466e29bfec203902'
poster = 'https://image.tmdb.org/t/p/w500'
fanart =  'https://image.tmdb.org/t/p/w1280'
tmdb_list = ['https://api.themoviedb.org/3/movie/now_playing'+api_key+'&language=en-US&page=1', 'https://api.themoviedb.org/3/discover/tv'+api_key+'&language=en-US&sort_by=popularity.desc&air_date.gte='+str(today)+'&page=1&timezone=America%2FNew_York&without_genres=16%2C10751%2C10762%2C10763%2C10764%2C10766%2C10767%2C210024&include_null_first_air_dates=false']



class Screensaver(xbmcgui.WindowXMLDialog):

    def __init__( self, *args, **kwargs):
        self.prev = None
        self.next = None
        self.isExiting = False
        self.cache = simplecache.SimpleCache()


    def onInit(self):
        self.getCache()


    def getJson(self):
        data = []
        for item in tmdb_list:
            request = Request(item)
            response_body = urlopen(request).read()
            response = json.loads(str(response_body))
            data.append(response['results'])

        data = data[0] + data[1]
        return data


    def getCache(self):
        data_cache = self.cache.get(addon_name + '.matJsonData')
        if data_cache:
            self.rotateItems(data_cache)
        else:
            data = self.getJson()
            self.cache.set(addon_name + '.matJsonData', data, expiration=datetime.timedelta(hours=24))   
            self.getCache()


    def rotateItems(self, data):
        while not monitor.abortRequested():
            self.next = choice(data)
            self.setItem(self.next)
            if monitor.waitForAbort(timer) == True or self.isExiting == True: break

    
    def getGenres(self, data, category):
        genres = []
        genre_type = movie_genres if category == 'movie' else tv_genres

        for genre in genre_type:
            if int(genre[1]) in data:
                genres.append(genre[0])

        return ' / '.join(genres)


    def setItem(self, data):
        self.getControl(2200).setImage(fanart + data['backdrop_path'])
        
        votes = float(data['vote_average'])
        self.getControl(3300).setLabel(str(votes))

        try:
            self.getControl(4400).setLabel(str(data['title']))
            self.getControl(6600).setLabel(self.getGenres(data['genre_ids'], 'movie'))
        except:
            self.getControl(4400).setLabel(str(data['name']))
            self.getControl(6600).setLabel(self.getGenres(data['genre_ids'], 'tvshow'))

        self.getControl(5500).setImage(poster + data['poster_path'])

        if not data['overview']:
            data['overview'] == 'No Information Available'

        self.getControl(7700).setLabel(str(data['overview']))


    def onAction(self, action):
        self.isExiting = True
        self.close()