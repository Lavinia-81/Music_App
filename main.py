from PyQt6.QtWidgets import *
from utils import songs
import random
from db_functions import *
from music import Ui_MusicApp
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QTimer, Qt, QUrl, QTime
from utils.context_menu import ContextMenu
from utils.playlist_manager import PlaylistManager
from utils.favourites_manager import FavouritesManager
from utils.delete_manager import DeleteManager
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QMainWindow




class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self, main_window=None):
        super().__init__()
        self.setupUi(self)
        self.window = QMainWindow()
        self.main_window = main_window if main_window is not None else self
        self.player = QMediaPlayer()
        self.stopped = False
        self.default_next()
        self.songs = []
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.favourites_manager = FavouritesManager(self, songs)
        self.context_menu = ContextMenu(self)
        self.playlist_manager = PlaylistManager(self)
        self.delete_manager = DeleteManager(self)
        self.player.mediaStatusChanged.connect(self.on_media_finished)

        with open("static/stylesheet.css", "r") as file:
            self.setStyleSheet(file.read())

        # Globals
        global stopped
        global looped
        global is_shuffled
        global slide_index

        stopped =False
        looped = False
        is_shuffled = False
        slide_index = 0

        # Context Menus
        self.playlist_context_menu()
        self.loaded_songs_context_menu()
        self.favourite_songs_context_menu()

        # Database Stuff
        create_database_or_database_table('favourites')
        self.favourites_manager.load_favourites_into_app()
        self.playlist_manager.load_playlists()


        # Create Player
        self.player = QMediaPlayer()
        self.initial_volume = 20
        self.audio_output.setVolume(self.initial_volume / 100)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f"{self.initial_volume}")

        # Slider Timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)
        self.music_slider.setEnabled(True)
        self.music_slider.setSingleStep(1000)


        # Connection
        # DEFAULT PAGE
        self.music_slider.sliderMoved.connect(lambda pos: self.player.setPosition(pos))
        self.player.mediaStatusChanged.connect(self.song_finished)
        self.player.mediaStatusChanged.connect(lambda status: print(f"Media status changed: {status}"))
        self.player.mediaStatusChanged.connect(self.on_media_finished)
        self.player.positionChanged.connect(self.music_slider.setValue)
        self.player.positionChanged.connect(self.check_position)
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.next_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.loop_one_btn.clicked.connect(self.loop_on_song)
        self.delete_selected_btn.clicked.connect(self.delete_manager.remove_selected_song)
        self.delete_all_songs_btn.clicked.connect(self.delete_manager.remove_all_songs)
        self.music_slider.sliderMoved.connect(self.move_slider)
        self.volume_dial.valueChanged.connect(self.set_volume)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_playlist)
        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlist_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)
        self.add_to_fav_btn.clicked.connect(self.favourites_manager.add_song_to_favourites)


        # Default Page Actions
        self.actionPlay.triggered.connect(self.play_song)
        self.actionPause_Unpause.triggered.connect(self.pause_and_unpause)
        self.actionNext.triggered.connect(self.next_song)
        self.actionPrevious.triggered.connect(self.previous_song)
        self.actionStop.triggered.connect(self.stop_song)


        # FAVOURITES
        self.delete_selected_favourite_btn.clicked.connect(self.favourites_manager.remove_song_from_favourites)
        self.delete_all_favourites_btn.clicked.connect(self.favourites_manager.remove_all_songs_from_favourites)

        # Favourite Actions
        self.actionAdd_Selected_to_Favourites.triggered.connect(self.favourites_manager.add_song_to_favourites)
        self.actionAdd_all_to_Favouries.triggered.connect(self.favourites_manager.add_all_songs_to_favourites)
        self.actionRemove_Selected_Favourite.triggered.connect(self.favourites_manager.remove_song_from_favourites)
        self.actionRemove_All_Favourites.triggered.connect(self.favourites_manager.remove_all_songs_from_favourites)

        # PLAYLISTS
        self.playlists_listWidget.itemDoubleClicked.connect(self.playlist_manager.show_playlist_content)
        self.new_playlist_btn.clicked.connect(self.playlist_manager.new_playlist)
        self.remove_selected_playlist_btn.clicked.connect(self.playlist_manager.delete_playlist)
        self.remove_all_playlists_btn.clicked.connect(self.playlist_manager.delete_all_playlists)
        self.add_to_playlist_btn.clicked.connect(self.playlist_manager.add_all_current_songs_to_a_playlist)
        try:
            self.load_selected_playlist_btn.clicked.connect(
                lambda: self.playlist_manager.load_playlist_songs_to_current_list(
                    self.playlists_listWidget.currentItem().text()
                )
            )

            self.actionLoad_Selected_Playlist.triggered.connect(
                lambda: self.playlist_manager.load_playlist_songs_to_current_list(
                    self.playlists_listWidget.currentItem().text()
                )
            )
        except Exception as e:
            print(f"Error connecting button: {e}")



        # # Playlist Actions
        self.actionSave_all_to_a_Playlist.triggered.connect(self.playlist_manager.add_all_current_songs_to_a_playlist)
        self.actionSave_Selected_to_a_Playlist.triggered.connect(self.playlist_manager.add_a_song_to_a_playlist)
        self.actionDelete_All_Playlists.triggered.connect(self.playlist_manager.delete_all_playlists)
        self.actionDelete_Selected_Playlist.triggered.connect(self.playlist_manager.delete_playlist)

        self.show()




    # Play song
    def play_song(self):
        try:
            current_selection = self.loaded_songs_listWidget.currentRow()
            current_song = songs.current_song_list[current_selection]

            self.audio_output = QAudioOutput()
            self.player = QMediaPlayer()
            self.player.setAudioOutput(self.audio_output)

            song_url = QUrl.fromLocalFile(current_song)
            self.player.setSource(song_url)
            self.player.play()

            self.current_song_name.setText(f"{os.path.basename(current_song)}")
            self.current_song_path.setText(f"{os.path.dirname(current_song)}")
        except Exception as e:
            print(f"play song error: {e}")


    # Pause and Unpause
    def pause_and_unpause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            print("Music paused")
        else:
            self.player.play()
            print("Music resumed")


    # Stop Song
    def stop_song(self):
        try:
            self.player.stop()
            print("Music stoped")
        except Exception as e:
            print(f"Stop song error: {e}")


    # Function to set the volume
    def set_volume(self):
        try:
            volume = self.volume_dial.value()
            self.player.audioOutput().setVolume(volume / 100)
            self.volume_label.setText(f"{volume}")
        except Exception as e:
            print(f"Volume change error: {e}")


    # Function to change the Volume
    def volume_change(self):
        try:
            self.initial_volume = self.volume_dial.value()
            self.audio_output.setVolume(
                self.initial_volume / 100)
            self.volume_label.setText(f"{self.initial_volume}")
        except Exception as e:
            print(f"Volume change error: {e}")


    # Remove One Song
    def remove_selected_song(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove selected Song',
                    'Playlist is empty'
                )
                return
            current_index = self.loaded_songs_listWidget.currentRow()
            self.loaded_songs_listWidget.takeItem(current_index)
            songs.current_song_list.pop(current_index)
        except Exception as e:
            print(f"Remove selected song error: {e}")


    # Function to Remove All Song
    def remove_all_songs(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove All Songs',
                    'The playlist is empty and there is nothing to remove.'
                )
                return

            question = QMessageBox.question(
                self, 'Remove All Songs',
                'This action will remove all songs from the list and cannot be undone.\n'
                'Do you want to continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if question == QMessageBox.StandardButton.Yes:
                self.stop_song()
                self.loaded_songs_listWidget.clear()
                songs.current_song_list.clear()
                print("All songs removed from the playlist.")

        except Exception as e:
            print(f"Error while removing all songs: {e}")


    # Function to Play Previous Song
    def previous_song(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                song_list = songs.current_song_list
                list_widget = self.loaded_songs_listWidget
            elif self.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
                list_widget = self.favourites_listWidget
            else:
                print("Invalid playlist index.")
                return

            song_index = list_widget.currentRow()

            if song_index <= 0:
                print("No previous song available.")
                return

            previous_index = song_index - 1
            previous_song = song_list[previous_index]

            song_url = QUrl.fromLocalFile(previous_song)
            self.player.setSource(song_url)
            self.player.play()

            list_widget.setCurrentRow(previous_index)
            self.current_song_name.setText(f"{os.path.basename(previous_song)}")
            self.current_song_path.setText(f"{os.path.dirname(previous_song)}")

            list_widget.update()

        except Exception as e:
            print(f"Previous Song error: {e}")


    # Function to Play Next Song
    def next_song(self):
        try:
            global looped
            global is_shuffled

            if is_shuffled:
                self.shuffled_next()
            elif looped:
                self.looped_next()
            else:
                self.default_next()

        except Exception as e:
            print(f"Next Song error: {e}")



    # Function to Check position
    def check_position(self, position):
        duration = self.player.duration()
        if duration > 0 and position >= duration - 1000:
            print("Position almost at end, waiting before next song...")
            QTimer.singleShot(500, self.next_song)

        self.default_next()

        def moveApp(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.initialPosition)
                self.initialPosition = event.globalPosition().toPoint()
                event.accept()

        self.title_frame.mouseMoveEvent = moveApp



    # Function to handle the mouse position
    def mousePressEvent(self, event):
        self.initialPosition = event.globalPos()


    # Finished Song
    def song_finished(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("Song finished. Moving to next.")
            self.next_song()
        else:
            print(f"Ignoring status: {status}")
            self.default_next()


    # Move Slider
    def move_slider(self):
        if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            return

        duration = self.player.duration()
        if duration > 0:
            self.music_slider.setMinimum(0)
            self.music_slider.setMaximum(duration)
            slider_position = self.player.position()
            self.music_slider.setValue(slider_position)


            current_time = QTime(0, 0).addMSecs(slider_position).toString("HH:mm:ss")
            song_duration = QTime(0, 0).addMSecs(duration).toString("HH:mm:ss")

            self.time_label.setText(f"{current_time} / {song_duration}")

        self.music_slider.repaint()
        self.music_slider.update()


    # Add songs
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add Songs to the app', directory=':\\',
            filter='Supported Files (*.mp3;*.mpeg;*.ogg;*.m4a;*.MP3;*.wma;*.acc;*.amr)'
        )
        if files:
            for file in files:
                songs.current_song_list.append(file)
                song_name = os.path.basename(file)
                item = QListWidgetItem(QIcon(r"utils/images/MusicListItem.png"),song_name)
                self.loaded_songs_listWidget.addItem(item)
                self.loaded_songs_listWidget.setViewMode(QListWidget.ViewMode.ListMode)


    # Function for Default Next
    def default_next(self):
        try:
            current_song_url = self.player.source().toLocalFile()

            if self.stackedWidget.currentIndex() == 0:
                song_list = songs.current_song_list
            elif self.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
            else:
                print("Invalid playlist index.")
                return

            if current_song_url not in song_list:
                print("Current song not found in list.")
                return

            # song_index = song_list.index(current_song_url)
            # next_index = song_index + 1
            song_index = song_list.index(current_song_url)
            next_index = (song_index + 1) % len(song_list)


            if next_index >= len(song_list):
                print("No next song available.")
                return

            next_song = song_list[next_index]
            song_url = QUrl.fromLocalFile(next_song)
            self.player.setSource(song_url)
            self.player.play()

            self.favourites_listWidget.setCurrentRow(next_index)
            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(f'{os.path.basename(next_song)}')
            self.current_song_path.setText(f'{os.path.dirname(next_song)}')

            self.favourites_listWidget.update()
            self.loaded_songs_listWidget.update()

        except Exception as e:
            print(f"Default Next error: {e}")


    # Loop Function
    def setup_looped_playback(self):
        self.player.mediaStatusChanged.connect(self.on_media_finished)


    # Media finished
    def on_media_finished(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("Song finished! Moving to next track...")
            self.default_next()

        elif self.player.mediaStatus() != QMediaPlayer.MediaStatus.LoadedMedia:
            print("Error: Media is not loaded yet!")
            return


    # Function to Handle Media Status Changes
    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadingMedia:
            print("Media is still loading, waiting before playback...")
            return

        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            print("Error: Invalid media file!")
            QMessageBox.warning(self, "Playback Error",
                                "The selected media file is invalid or corrupted.")
            return

        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("Song has finished playing. Moving to the next track...")
            self.next_song()


    # Function to Loop Next

    def looped_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                current_song_url = self.player.source().toLocalFile()
                song_list = songs.current_song_list
            elif self.stackedWidget.currentIndex() == 2:
                current_song_url = self.player.source().toLocalFile()
                song_list = songs.favourites_song_list
            else:
                print("Invalid playlist index.")
                return

            if current_song_url not in song_list:
                print("Current song not found in list.")
                return

            song_index = song_list.index(current_song_url)
            next_index = (song_index + 1) % len(song_list)

            next_song = song_list[next_index]
            song_url = QUrl.fromLocalFile(next_song)
            self.player.setSource(song_url)
            self.player.play()

            self.loaded_songs_listWidget.setCurrentRow(next_index)
            print(f"Now playing: {next_song}")

            self.current_song_name.setText(os.path.basename(next_song))
            self.current_song_path.setText(os.path.dirname(next_song))

        except Exception as e:
            print(f"Looped Next error: {e}")



    # Shuffled Next Function
    def shuffled_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                song_list = songs.current_song_list
            elif self.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
            else:
                print("Invalid playlist index.")
                return

            if not song_list:
                print("Song list is empty.")
                return

            next_index = random.randint(0, len(song_list) - 1)
            next_song = song_list[next_index]

            song_url = QUrl.fromLocalFile(next_song)
            self.player.setSource(song_url)
            self.player.play()

            if self.stackedWidget.currentIndex() == 0:
                self.loaded_songs_listWidget.setCurrentRow(next_index)
            elif self.stackedWidget.currentIndex() == 2:
                self.favourites_listWidget.setCurrentRow(next_index)

            self.current_song_name.setText(os.path.basename(next_song))
            self.current_song_path.setText(os.path.dirname(next_song))

            print(f"Now playing: {next_song}")

        except Exception as e:
            print(f"Shuffled Next error: {e}")


    # Function to toggle loop on the current song
    def loop_on_song(self):
        try:
            global looped
            global is_shuffled

            if not looped:
                looped = True
                self.shuffle_songs_btn.setEnabled(False)
                print("Looping is now enabled.")
            else:
                looped = False
                self.shuffle_songs_btn.setEnabled(True)
                print("Looping is now disabled.")
        except Exception as e:
            print(f"Looping song error: {e}")


    # Function to shuffle the playlist
    def shuffle_playlist(self):
        try:
            global looped
            global is_shuffled

            if not is_shuffled:
                is_shuffled = True
                self.loop_one_btn.setEnabled(False)
                print("Shuffling is now enabled.")
            else:
                is_shuffled = False
                self.loop_one_btn.setEnabled(True)
                print("Shuffling is now disabled.")
        except Exception as e:
            print(f"Shuffling song error: {e}")



    # FUNCTIONS TO SWITCH TABS
    # Switch to Favourite
    def switch_to_favourites_tab(self):
        self.stackedWidget.setCurrentIndex(2)

    # Switch to Playlist tab
    def switch_to_playlist_tab(self):
        self.stackedWidget.setCurrentIndex(1)

    # Switch to Songs List tab
    def switch_to_songs_tab(self):
        self.stackedWidget.setCurrentIndex(0)



    # CONTEXT MENUS
    # Playlist Context Menu
    def playlist_context_menu(self):
        self.playlists_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.playlists_listWidget.addAction(self.actionLoad_Selected_Playlist)
        separator = QAction(self)
        separator.setSeparator(True)
        self.playlists_listWidget.addAction(self.actionDelete_Selected_Playlist)
        self.playlists_listWidget.addAction(self.actionDelete_All_Playlists)


    # Loaded Songs Context Menu
    def loaded_songs_context_menu(self):
        self.loaded_songs_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.loaded_songs_listWidget.addAction(self.actionPlay)
        self.loaded_songs_listWidget.addAction(self.actionPause_Unpause)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionPrevious)
        self.loaded_songs_listWidget.addAction(self.actionNext)
        self.loaded_songs_listWidget.addAction(self.actionStop)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionAdd_Selected_to_Favourites)
        self.loaded_songs_listWidget.addAction(self.actionAdd_all_to_Favouries)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionSave_Selected_to_a_Playlist)
        self.loaded_songs_listWidget.addAction(self.actionSave_all_to_a_Playlist)


     # Loaded Songs Context Menu
    def favourite_songs_context_menu(self):
        self.favourites_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.favourites_listWidget.addAction(self.actionRemove_Selected_Favourite)
        self.favourites_listWidget.addAction(self.actionRemove_All_Favourites)
