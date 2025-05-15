import time
from PyQt6.QtWidgets import *
from utils import songs
import random
from db_functions import *
from music import Ui_MusicApp
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QTimer, Qt, QUrl, QTime
from utils.context_menu import ContextMenu
from utils.playlist_manager import PlaylistManager
from utils.favourites_manager import FavouritesManager
from utils.delete_manager import DeleteManager




class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self, main_window=None):
        super().__init__()
        self.setupUi(self) # Set up the UI
        self.main_window = main_window if main_window is not None else self  # Define main window
        self.player = QMediaPlayer()  # Initialize the media player
        self.stopped = False  # Track if music is stopped
        self.default_next()  # Set default song navigation
        self.looped_next()
        self.shuffled_next()
        self.songs = []
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)   # Connect media player to audio output

        self.favourites_manager = FavouritesManager(self, songs)
        self.context_menu = ContextMenu(self)
        self.playlist_manager = PlaylistManager(self)
        self.delete_manager = DeleteManager(self)

        # Apply styles from external CSS file
        with open("static/stylesheet.css", "r") as file:
            self.setStyleSheet(file.read())

        # Initial position of the window
        self.initialPosition = self.pos()

        # Define global variables for playback control
        global stopped
        global looped
        global is_shuffled
        global slide_index

        stopped =False
        looped = False
        is_shuffled = False
        slide_index = 0

        # Set up context menus for different sections
        self.playlist_context_menu()
        self.loaded_songs_context_menu()
        self.favourite_songs_context_menu()

        # Initialize the database and load saved data
        create_database_or_database_table('favourites')
        self.favourites_manager.load_favourites_into_app()
        self.playlist_manager.load_playlists()


        # Configure media player settings
        self.player = QMediaPlayer()
        self.initial_volume = 20
        self.audio_output.setVolume(self.initial_volume / 100)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f"{self.initial_volume}")

        # Setup timer for music slider update
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)
        self.music_slider.setEnabled(True)
        self.music_slider.setSingleStep(1000)


        # Connect UI elements to their respective functions
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
        # self.music_slider.sliderMoved.connect(self.move_slider)
        self.volume_dial.valueChanged.connect(self.set_volume)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_playlist)
        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlist_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)
        self.add_to_fav_btn.clicked.connect(self.favourites_manager.add_song_to_favourites)
        self.music_slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.music_slider.value()))

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
        self.add_to_playlist_btn.clicked.connect(self.playlist_manager.add_currently_playing_to_a_playlist)
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


        def moveApp(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.initialPosition)
                self.initialPosition = event.globalPos()
                event.accept()

        self.title_frame.mouseMoveEvent = lambda event: moveApp(event)


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < self.title_frame.height():
            self.initialPosition = event.globalPos()


    # Play song
    def play_song(self):
        try:
            current_selection = self.loaded_songs_listWidget.currentRow()  # Get the selected song index
            current_song = songs.current_song_list[current_selection]

            self.audio_output = QAudioOutput()  # Initialize audio output
            self.player = QMediaPlayer() # Initialize media player
            self.player.setAudioOutput(self.audio_output) # Set audio output for the player

            song_url = QUrl.fromLocalFile(current_song) # Convert song path to a URL
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
            if self.loaded_songs_listWidget.count() == 0:  # Check if playlist is empty
                QMessageBox.information(
                    self, 'Remove selected Song',
                    'Playlist is empty'
                )
                return
            current_index = self.loaded_songs_listWidget.currentRow() # Get selected song index
            self.loaded_songs_listWidget.takeItem(current_index) # Remove song from UI list
            songs.current_song_list.pop(current_index) # Remove song from the stored list
        except Exception as e:
            print(f"Remove selected song error: {e}")


    # Function to Remove All Song
    def remove_all_songs(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:  # Check if the playlist is empty
                QMessageBox.information(
                    self, 'Remove All Songs',
                    'The playlist is empty and there is nothing to remove.'
                )
                return

            # Ask user for confirmation before deleting all songs
            question = QMessageBox.question(
                self, 'Remove All Songs',
                'This action will remove all songs from the list and cannot be undone.\n'
                'Do you want to continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            # If user confirms, remove all songs and clear playlist
            if question == QMessageBox.StandardButton.Yes:
                self.stop_song()
                self.loaded_songs_listWidget.clear() # Clear UI song list
                songs.current_song_list.clear()   # Clear internal song list
                print("All songs removed from the playlist.")

        except Exception as e:
            print(f"Error while removing all songs: {e}")


    # Function to Play Previous Song
    def previous_song(self):
        try:
            # Determine which playlist is active
            if self.stackedWidget.currentIndex() == 0:
                song_list = songs.current_song_list
                list_widget = self.loaded_songs_listWidget
            elif self.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
                list_widget = self.favourites_listWidget
            else:
                print("Invalid playlist index.")
                return

            song_index = list_widget.currentRow() # Get current song index

            if song_index <= 0:
                print("No previous song available.")
                return

            previous_index = song_index - 1 # Calculate previous song index
            previous_song = song_list[previous_index] # Get previous song
            # Load and play previous song
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
        duration = self.player.duration() # Get song duration
        if duration > 0 and position >= duration - 1000:
            print("Position almost at end, waiting before next song...")
            QTimer.singleShot(500, lambda: self.next_song())

        self.default_next()


        # def moveApp(event):
        #     if event.buttons() == Qt.MouseButton.LeftButton:
        #         self.move(self.pos() + event.globalPosition().toPoint() - self.initialPosition)
        #         self.initialPosition = event.globalPosition().toPoint()
        #         event.accept()
        #
        # self.title_frame.mouseMoveEvent = moveApp


    # Song Finished Function
    def song_finished(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("Song finished. Moving to next.")
            self.next_song()


    # Move Slider
    def move_slider(self):
        if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            return

        duration = self.player.duration() # Get song duration
        if duration > 0:
            # Update slider min and max range
            self.music_slider.setMinimum(0)
            self.music_slider.setMaximum(duration)
            slider_position = self.player.position() # Get current song position
            self.music_slider.setValue(slider_position) # Update slider position


            current_time = time.strftime("%H:%M:%S", time.localtime(self.player.position() / 1000))
            song_duration = time.strftime("%H:%M:%S", time.localtime(self.player.duration() / 1000))

            self.time_label.setText(f"{current_time} / {song_duration}") # Update time label


    # Add songs
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add Songs to the app', directory=':\\',
            filter='Supported Files (*.mp3;*.mpeg;*.ogg;*.m4a;*.MP3;*.wma;*.acc;*.amr)' # File filter for supported audio formats
        )
        if files:
            for file in files:
                songs.current_song_list.append(file)  # Add song to the playlist list
                song_name = os.path.basename(file) # Extract song name from file path
                item = QListWidgetItem(QIcon(r"utils/images/MusicListItem.png"),song_name) # Create list item with icon
                self.loaded_songs_listWidget.addItem(item) # Add song to UI list
                self.loaded_songs_listWidget.setViewMode(QListWidget.ViewMode.ListMode) # Set list view mode


    # Function to play the next song in default order
    def default_next(self):
        try:
            current_song_url = self.player.source().toLocalFile() # Get current song URL

            # Determine which song list to use based on current tab index
            if self.stackedWidget.currentIndex() == 0:
                song_list = songs.current_song_list
            elif self.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
            else:
                print("Invalid playlist index.")
                return

            # Ensure the current song exists in the list
            if current_song_url not in song_list:
                # print("Current song not found in list.")
                return

            song_index = song_list.index(current_song_url)
            next_index = song_index + 1
            # song_index = song_list.index(current_song_url)
            # next_index = (song_index + 1) % len(song_list)


            if next_index >= len(song_list):
                print("No next song available.")
                return

            next_song = song_list[next_index] # Retrieve next song
            song_url = QUrl.fromLocalFile(next_song) # Convert file path to URL
            self.player.setSource(song_url)
            self.player.play()
            print(f"Setting next song: {next_song}")  # Debug

            self.favourites_listWidget.setCurrentRow(next_index)
            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(f'{os.path.basename(next_song)}') # Display song name
            self.current_song_path.setText(f'{os.path.dirname(next_song)}') # Display song path

            self.favourites_listWidget.update()
            self.loaded_songs_listWidget.update()

        except Exception as e:
            print(f"Default Next error: {e}")


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
                # print("Current song not found in list.")
                return

            song_index = song_list.index(current_song_url) # Get current song index
            next_index = (song_index + 1) % len(song_list) # Loop to first song if at the end

            next_song = song_list[next_index] # Retrieve next song
            song_url = QUrl.fromLocalFile(next_song) # Convert to URL
            self.player.setSource(song_url) # Load next song
            self.player.play()

            self.loaded_songs_listWidget.setCurrentRow(next_index)
            print(f"Now playing: {next_song}")

            self.current_song_name.setText(os.path.basename(next_song)) # Display song name
            self.current_song_path.setText(os.path.dirname(next_song)) # Display song path

        except Exception as e:
            print(f"Looped Next error: {e}")



    # Function to shuffle and play the next song
    def shuffled_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                song_list = songs.current_song_list
            elif self.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
            else:
                print("Invalid playlist index.")
                return

            if not song_list: # Ensure song list is not empty
                # print("Song list is empty.")
                return

            next_index = random.randint(0, len(song_list) - 1) # Select a random song
            next_song = song_list[next_index]

            song_url = QUrl.fromLocalFile(next_song) # Convert file path to URL
            self.player.setSource(song_url)   # Load song
            self.player.play()

            if self.stackedWidget.currentIndex() == 0:
                self.loaded_songs_listWidget.setCurrentRow(next_index)
            elif self.stackedWidget.currentIndex() == 2:
                self.favourites_listWidget.setCurrentRow(next_index)

            self.current_song_name.setText(os.path.basename(next_song)) # Display song name
            self.current_song_path.setText(os.path.dirname(next_song)) # Display song path

            print(f"Now playing: {next_song}")

        except Exception as e:
            print(f"Shuffled Next error: {e}")


    # Function to toggle looping for the current song
    def loop_on_song(self):
        try:
            global looped
            global is_shuffled

            if not looped: # Enable loop mode
                looped = True
                self.shuffle_songs_btn.setEnabled(False)
                print("Looping is now enabled.")
            else:  # Disable loop mode
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
        separator.setSeparator(True) # Add separator for better organization
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
