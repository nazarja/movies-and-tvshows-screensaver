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
highlight_color = [ '800385b5', '80b80419', '80bd069e', '80c25808', '80c7b10a', '8025D366', '80810ccf'][int(addon.getSetting('HighlightColor'))]
hide_topbar = 'hide' if addon.getSetting('HideTopbar') == 'true' else 'show'
hide_information = 'hide' if addon.getSetting('HideInformation') == 'true' else 'show'
hide_overlay = 'hide' if addon.getSetting('HideOverlay') == 'true' else 'show'
darker_overlay = 'darker' if addon.getSetting('DarkerOverlay') == 'true' else 'lighter'
no_color = 'nocolor' if addon.getSetting('NoColor') == 'true' else 'color'


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
        self.window_id.setProperty('highlight_color', highlight_color)
        self.window_id.setProperty('hide_information', hide_information)
        self.window_id.setProperty('hide_topbar', hide_topbar)
        self.window_id.setProperty('hide_overlay', hide_overlay)
        self.window_id.setProperty('darker_overlay', darker_overlay)
        self.window_id.setProperty('no_color', no_color)
        self.getCache()


    def getJson(self):
        data = []
        for item in tmdb_list:
            request = Request(item)
            response_body = urlopen(request)
            response = json.load(response_body)
            data.append(response['results'])
        return data[0] + data[1] + data[2] + data[3]


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
        genre_type = movie_genres if category == 'movie' else tv_genres
        genres = []
        for genre in genre_type:
            if int(genre[1]) in data:
                genres.append(genre[0])
        return ' / '.join(genres)


    def setItem(self, data):

        if not data['backdrop_path']:
            self.rotateItems()

        if not data['overview']:
            data['overview'] == 'No Information Available'

        self.getControl(2200).setImage(fanart + data['backdrop_path'])
        self.getControl(5500).setImage(poster + data['poster_path'])

        try: 
            self.getControl(3300).setLabel(str(float(data['vote_average'])))
        except:
            self.getControl(3300).setLabel('0.0')
            
        try:
            self.getControl(4400).setLabel(data['title'])
            self.getControl(6600).setLabel(self.getGenres(data['genre_ids'], 'movie'))
        except:
            self.getControl(4400).setLabel(data['name'])
            self.getControl(6600).setLabel(self.getGenres(data['genre_ids'], 'tvshow'))

        try:
            self.getControl(7700).setLabel(data['overview'])
        except:
             self.getControl(7700).setLabel('No Information Available')


    def onAction(self, action):
        self.isExiting = True
        self.close()