from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtMultimedia import QMediaPlayer
from utils.playlist_popup import PlaylistDialog
from PyQt6.QtGui import QPixmap
from db_functions import *
import os
from utils import songs



class ContextMenu:
    def __init__(self, main_window):
        self.main_window = main_window



    def playlist_context_menu(self):
        self.main_window.playlists_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.main_window.playlists_listWidget.addAction(self.main_window.actionLoad_Selected_Playlist)

        separator = QAction(self.main_window)
        separator.setSeparator(True)
        self.main_window.playlists_listWidget.addAction(separator)

        self.main_window.playlists_listWidget.addAction(self.main_window.actionDelete_Selected_Playlist)
        self.main_window.playlists_listWidget.addAction(self.main_window.actionDelete_All_Playlists)

    def loaded_songs_context_menu(self):
        self.main_window.loaded_songs_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

        self.main_window.loaded_songs_listWidget.addAction(self.main_window.actionPlay)
        self.main_window.loaded_songs_listWidget.addAction(self.main_window.actionPause_Unpause)

        separator = QAction(self.main_window)
        separator.setSeparator(True)
        self.main_window.loaded_songs_listWidget.addAction(separator)

        self.main_window.loaded_songs_listWidget.addAction(self.main_window.actionPrevious)
        self.main_window.loaded_songs_listWidget.addAction(self.main_window.actionNext)
        self.main_window.loaded_songs_listWidget.addAction(self.main_window.actionStop)

    def slideshow(self):
        images_path = os.path.join(os.getcwd(), os.path.join('', 'bg_imgs'))
        images = os.listdir(images_path)
        images.remove('bg_overlay.png')
        global slide_index

        next_slide = images[slide_index]
        next_image = QPixmap(os.path.join(images_path, f'{next_slide}'))
        self.main_window.background_image.setPixmap(next_image)
        slide_index += 1

    def favourites_songs_context_menu(self):
        self.main_window.favourites_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.main_window.favourites_listWidget.addAction(self.main_window.actionRemove_Selected_Favourite)
        self.main_window.favourites_listWidget.addAction(self.main_window.actionRemove_All_Favourites)