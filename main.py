import os
import time
import random
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import *
import songs
from db_functions import add_song_to_database_table
from music import Ui_MusicApp
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QMessageBox


class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.default_next()
        self.stopped = False

        # Globals
        global stopped
        global looped
        global is_shuffled

        # stopped =False
        looped = False
        is_shuffled = False


        # # Database Stuff
        # add_song_to_database_table('favorites')


        # Create Player
        self.player = QMediaPlayer()

        self.initial_volume = 20
        self.audio_output.setVolume(self.initial_volume / 100)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f"{self.initial_volume}")

        # Slider Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_slider)
        self.timer.start(1000)

        # Connection
        # DEFAULT PAGE
        self.player.positionChanged.connect(self.check_position)
        self.player.mediaStatusChanged.connect(self.song_finished)
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.volume_dial.valueChanged.connect(self.volume_change)
        self.next_btn.clicked.connect(self.next_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_playlist)
        self.loop_one_btn.clicked.connect(self.loop_on_song)
        self.delete_selected_btn.clicked.connect(self.remove_selected_song)
        self.delete_all_songs_btn.clicked.connect(self.remove_all_songs)
        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlist_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)

        self.music_slider.sliderMoved.connect(lambda position: self.player.setPosition(position))
        self.add_to_fav_btn.clicked.connect(self.add_song_to_favourites)



        self.show()

    def song_finished(self, status):
        print(f"Media status changed: {status}")  # Debugging output
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("EndOfMedia detected. Playing next song...")
            self.next_song()
        else:
            print(f"Unhandled status: {status}")

    def check_position(self, position):
        duration = self.player.duration()
        if duration > 0 and position >= duration - 1000:
            print("Position almost at end, going to the next song...")
            self.next_song()



    # Function to move the slider
    def move_slider(self):
        try:
            if self.stopped:
                return

            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.music_slider.setMinimum(0)
                self.music_slider.setMaximum(self.player.duration())
                slider_position = self.player.position()
                self.music_slider.setValue(slider_position)

                # Change time labels
                current_time = time.strftime("%H:%M:%S", time.localtime(self.player.position() / 1000))
                song_duration = time.strftime("%H:%M:%S", time.localtime(self.player.duration() / 1000))
                self.time_label.setText(f"{current_time} / {song_duration}")

                # print(f"Duration: {self.player.duration()}")
                # print(f"Current Position: {slider_position}")
        except Exception as e:
            print(f"Error in move_slider: {e}")


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


    # Function to change the Volume
    def volume_change(self):
        try:
            self.initial_volume = self.volume_dial.value()
            self.audio_output.setVolume(
                self.initial_volume / 100)
            self.volume_label.setText(f"{self.initial_volume}")
        except Exception as e:
            print(f"Volume change error: {e}")



    def default_next(self):
        try:
            # Get the current index of the selected song
            current_index = self.loaded_songs_listWidget.currentRow()
            if current_index == -1:
                print("No song is currently selected.")
                return

            # Increment the index to go to the next song
            next_index = current_index + 1

            # Check if the next index is within bounds
            if next_index >= len(songs.current_song_list):
                print("No next song")
                return

            # Retrieve the next song and its URL
            next_song = songs.current_song_list[next_index]
            song_url = QUrl.fromLocalFile(next_song)

            # Play the next song
            self.player.setSource(song_url)
            self.player.play()

            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(os.path.basename(next_song))
            self.current_song_path.setText(os.path.dirname(next_song))

            print(f"Now playing: {next_song}")

        except Exception as e:
            print(f"Default Next error: {e}")


    def looped_next(self):
        try:
            current_index = self.loaded_songs_listWidget.currentRow()
            if current_index == -1:
                print("No song is currently selected.")
                return

            # Increment index to move to the next song
            next_index = current_index + 1

            # Check if the next index is valid, loop back to the beginning if it exceeds the list
            if next_index >= len(songs.current_song_list):
                next_index = 0  # Loop back to the first song

            song = songs.current_song_list[next_index]
            song_url = QUrl.fromLocalFile(song)

            self.player.setSource(song_url)
            self.player.play()

            # Update UI components and select the next song in the list
            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(os.path.basename(song))
            self.current_song_path.setText(os.path.dirname(song))

            print(f"Now playing: {song}")
        except Exception as e:
            print(f"Looped Next error: {e}")


    def shuffled_next(self):
        try:
            # Generate a random index within the range of the song list
            next_index = random.randint(0, len(songs.current_song_list) - 1)

            # Fetch the next song using the generated random index
            next_song = songs.current_song_list[next_index]
            song_url = QUrl.fromLocalFile(next_song)

            # Set the source and play the song
            self.player.setSource(song_url)
            self.player.play()

            # Update the UI components to reflect the change
            self.loaded_songs_listWidget.setCurrentRow(next_index)
            self.current_song_name.setText(os.path.basename(next_song))
            self.current_song_path.setText(os.path.dirname(next_song))

            print(f"Now playing: {next_song}")
        except Exception as e:
            print(f"Shuffled Next error: {e}")


    # Play Next Song
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


    # Play Previous Song
    def previous_song(self):
        try:
            song_index = self.loaded_songs_listWidget.currentRow()
            previous_index = song_index - 1
            previous_song = songs.current_song_list[previous_index]
            song_url = QUrl.fromLocalFile(previous_song)
            self.player.setSource(song_url)
            self.player.play()
            self.loaded_songs_listWidget.setCurrentRow(previous_index)

            self.current_song_name.setText(f"{os.path.basename(previous_song)}")
            self.current_song_path.setText(f"{os.path.dirname(previous_song)}")

        except Exception as e:
            print(f"Next Song error")

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


    # Remove All Song
    def remove_all_songs(self):
        try:
            # Check if the playlist is empty
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self,
                    'Remove All Songs',
                    'The playlist is empty and there is nothing to remove.'
                )
                return

            # Show a confirmation dialog
            question = QMessageBox.question(
                self,
                'Remove All Songs',
                'This action will remove all songs from the list and cannot be undone.\n'
                'Do you want to continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            # If the user confirms, clear the playlist
            if question == QMessageBox.StandardButton.Yes:
                # Ensure stop_song is properly defined to stop playback
                self.stop_song()
                self.loaded_songs_listWidget.clear()
                songs.current_song_list.clear()
                print("All songs removed from the playlist.")

        except Exception as e:
            print(f"Error while removing all songs: {e}")


    # FUNCTIONS TO SWITCH TABS
    # Switch to Favourite
    def switch_to_favourites_tab(self):
        self.stackedWidget.setCurrentIndex(2)

    # Switch to Playlist tab
    def switch_to_playlist_tab(self):
        self.stackedWidget.setCurrentIndex(1)

    # Switch to Songs tab
    def switch_to_songs_tab(self):
        self.stackedWidget.setCurrentIndex(0)


    # FAVOURITE FUNCTIONS
    # Add song to favourites
    def add_song_to_favourites(self):
        current_index = self.loaded_songs_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Add Songs to Favourites',
                'Select a song to add to favourites')
            return
        try:
            song = songs.current_song_list[current_index]
            add_song_to_database_table(song=f"{song}", table='favorites')  # Nu 'favourites'
            QMessageBox.information(
                self, 'Add Songs to Favourites',
                f'{os.path.basename(song)} was successfully added to favourites')

        except Exception as e:
            print(f"Adding song to favourites error: {e}")


