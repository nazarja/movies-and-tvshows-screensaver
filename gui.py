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


addon = xbmcaddon.Addon('script.screensaver.moviesandtvshows')
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')
monitor = xbmc.Monitor()


timer = [10,15,20,30,45,60][int(addon.getSetting("RotateTime"))]
hide_overlay = 'hide' if addon.getSetting('HideOverlay') == 'true' else 'show'
colors = [ '800385b5', '80b80419', '80bd069e', '80c25808', '80c7b10a', '8022cc0c', '80810ccf']
highlight_color = colors[int(addon.getSetting('HighlightColor'))]

date = (datetime.datetime.utcnow() - datetime.timedelta(hours = 12))
today = (date).strftime('%Y-%m-%d')
current_year = (date).strftime('%Y')
previous_year = str(int((date).strftime('%Y')) - 1)


api_key = '?api_key=d41fd9978486321b466e29bfec203902'
poster = 'https://image.tmdb.org/t/p/w500'
fanart =  'https://image.tmdb.org/t/p/w1280'
tmdb_list = [
    'https://api.themoviedb.org/3/movie/now_playing'+api_key+'&language=en-US&page=1',
    'https://api.themoviedb.org/3/discover/movie'+api_key+'&language=en-US&sort_by=vote_count.desc&include_adult=false&include_video=false&page=1&primary_release_date.gte='+previous_year+'&primary_release_date.lte='+current_year+'&without_genres=16%2C10751%2C10762%2C10763%2C10764%2C10766%2C10767%2C210024',
    'https://api.themoviedb.org/3/discover/tv'+api_key+'&language=en-US&sort_by=popularity.desc&air_date.gte='+str(today)+'&page=1&timezone=America%2FNew_York&without_genres=16%2C10751%2C10762%2C10763%2C10764%2C10766%2C10767%2C210024&include_null_first_air_dates=false',
    'https://api.themoviedb.org/3/discover/tv'+api_key+'&language=en-US&sort_by=popularity.desc&first_air_date.gte='+previous_year+'&page=1&timezone=America%2FNew_York&without_genres=16%2C10751%2C10762%2C10763%2C10764%2C10766%2C10767%2C210024&include_null_first_air_dates=false'     
]



class Screensaver(xbmcgui.WindowXMLDialog):

    def __init__( self, *args, **kwargs):
        self.next = None
        self.isExiting = False
        self.window_id = None
        self.cache = simplecache.SimpleCache()


    def onInit(self):
        self.window_id = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.window_id.setProperty('hide_overlay', hide_overlay)
        self.window_id.setProperty('highlight_color', highlight_color)
        self.getCache()


    def getJson(self):
        data = []
        for item in tmdb_list:
            request = Request(item)
            response_body = urlopen(request)
            response = json.load(response_body)
            data.append(response['results'])

        data = data[0] + data[1] + data[2] + data[3]
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

        try:
            self.getControl(7700).setLabel(data['overview'])
        except:
             self.getControl(7700).setLabel('No Information Available')


    def onAction(self, action):
        self.isExiting = True
        self.close()