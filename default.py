############################################
#   CREDITS: 
#   - zag2me For the screensaver starter example
#   - Lunatixz: For learning from his google earth screensaver code
#   - jurialmunkey: For assets from Aura and styling inspiration
#   - marcelveldt: For assets from image-overlays pack
#     Thanks!
############################################

import xbmc
import xbmcgui
import xbmcaddon
import sys
import gui

addon = xbmcaddon.Addon('script.screensaver.tmdbss')
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')


# run
if __name__ == '__main__':

    # start
    screensaver_gui = gui.Screensaver( 'default.xml', addon_path, 'default')
    screensaver_gui.doModal()

    # exit
    del screensaver_gui
    sys.modules.clear()
