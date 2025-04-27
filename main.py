import os
import time

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import *
import songs
from music import Ui_MusicApp
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput #, QMediaContent

from PyQt6.QtCore import QUrl, QTimer

class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.stopped = False

        # Globals
        global stopped
        global looped
        global is_shuffeld
        looped = False
        is_shuffeld = False

        # Create Player
        self.player = QMediaPlayer()

        self.initial_volume = 20
        self.audio_output.setVolume(self.initial_volume / 100)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f"{self.initial_volume}")


        # Slider Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_slider)
        self.timer.start(1000)  # Actualizare la fiecare secundă


        # Connection
        # DEFAULT PAGE
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.volume_dial.valueChanged.connect(self.volume_change)

        self.show()


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

                print(f"Duration: {self.player.duration()}")
                print(f"Current Position: {slider_position}")
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