from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox, QInputDialog
from PyQt6.QtGui import QIcon
import os.path

from PyQt6.uic.properties import QtWidgets

from db_functions import *
from utils.playlist_popup import PlaylistDialog
from utils import songs


class PlaylistManager:
    def __init__(self, main_window):
        self.main_window = main_window


    # Load Playlist
    def load_playlists(self):
        try:
            playlists = get_playlist_tables()
            if not playlists or not isinstance(playlists, list):
                print("No playlists found.")
                return

            if "favourites" in playlists:
                playlists.remove("favourites")
            self.main_window.playlists_listWidget.clear()

            for playlist in playlists:
                item = QListWidgetItem(QIcon(r"utils/images/dialog-music.png"), playlist)
                self.main_window.playlists_listWidget.addItem(item)

            print(f"Loaded {len(playlists)} playlists.")

        except Exception as e:
            print(f"Error loading playlists: {e}")


    # Create new playlist
    def new_playlist(self):
        try:
            existing = get_playlist_tables() # Get existing playlist names
            name, ok = QInputDialog.getText(self.main_window, "Create new playlist", "Enter playlist name")

            # Validate playlist name (must not contain invalid characters)
            if not ok or not name.strip() or any(c in name for c in r'\/:*?"<>|'):
                QMessageBox.information(self.main_window, "Name Error", "Invalid playlist name.")
                return

            # If playlist does not exist, create it
            if name not in existing:
                create_database_or_database_table(name)  # Create new database table for playlist
                self.load_playlists()
                print(f"Playlist '{name}' created successfully.")
            else:
                # Ask user whether they want to replace an existing playlist
                caution = QMessageBox.question(
                    self.main_window, "Replace Playlist",
                    f"A playlist with name '{name}' already exists.\nDo you want to continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if caution == QMessageBox.StandardButton.Yes:
                    delete_database_table(name)  #  Delete existing playlist
                    create_database_or_database_table(name)  # Create a new one
                    self.load_playlists()
                    print(f"Playlist '{name}' replaced successfully.")

        except Exception as e:
            print(f"Error creating new playlist: {e}")


    # Delete a playlist
    def delete_playlist(self):
        try:
            selected_item = self.main_window.playlists_listWidget.currentItem()   # Get selected playlist
            if selected_item is None:  # If nothing is selected, show a message
                QMessageBox.information(self.main_window, "Delete Playlist", "No playlist selected.")
                return

            playlist = selected_item.text().strip() # Get playlist name

            if not playlist: # Ensure the playlist name is valid
                QMessageBox.information(self.main_window, "Delete Playlist", "Invalid playlist name.")
                return

            # Confirm deletion with user
            confirmation = QMessageBox.question(
                self.main_window, "Delete Playlist",
                f"Are you sure you want to delete the playlist '{playlist}'? This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirmation == QMessageBox.StandardButton.Yes:
                delete_database_table(playlist)
                self.load_playlists()
                print(f"Deleted playlist '{playlist}'.")
        except Exception as e:
            print(f"Error deleting playlist: {e}")


    # Delete all playlists except "favourites"
    def delete_all_playlists(self):
        try:
            playlists = get_playlist_tables()
            if "favourites" in playlists:
                playlists.remove("favourites") # Keep favourites playlist

            caution = QMessageBox.question(
                self.main_window, "Delete all Playlists",
                "This action will delete all playlists and it cannot be reversed.\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if caution == QMessageBox.StandardButton.Yes:
                for playlist in playlists:
                    delete_database_table(playlist)

                self.load_playlists()

                print("All playlists (except favourites) have been deleted.")
        except Exception as e:
            print(f"Error deleting all playlists: {e}")


    # Add a song to a selected playlist
    def add_a_song_to_a_playlist(self):
        options = get_playlist_tables()  # Get available playlists
        if "favourites" in options:
            options.remove("favourites")  # Exclude favourites

        options.insert(0, "--Click to Select--")  # Default selection prompt

        # Prompt user to select a playlist
        playlist, ok = QInputDialog.getItem(
            self.main_window, "Add song to playlist",
            "Choose the desired playlist", options, editable=False)

        if not ok or playlist == "--Click to Select--":  # Ensure valid selection
            QMessageBox.information(
                self.main_window, "Add song to playlist",
                "No playlist was selected.")
            return

        try:
            current_index = self.main_window.loaded_songs_listWidget.currentRow()
            song = songs.current_song_list[current_index]

            if not song.strip():  # Validate song name
                raise ValueError("Song name is empty!")
        except Exception as e:
            QMessageBox.information(self.main_window, "Unsuccessful", "No song was selected.")
            return

        add_song_to_database_table(song=song, table=playlist)  # Add song to playlist
        self.load_playlists()

        print(f"Added '{song}' to playlist '{playlist}'.")  # Debugging output


    # Add all current songs to a playlist
    def add_all_current_songs_to_a_playlist(self):
        options = get_playlist_tables()  # Get available playlists
        if "favourites" in options:
            options.remove("favourites")  # Exclude favourites

        options.insert(0, "--Click to Select--")  # Default selection prompt

        # Prompt user to select a playlist
        playlist, ok = QInputDialog.getItem(
            self.main_window, "Add song to playlist",
            "Choose the desired playlist", options, editable=False)

        if not ok or playlist == "--Click to Select--":  # Validate selection
            QMessageBox.information(self.main_window, "Add song to playlist", "No playlist was selected")
            return

        if not songs.current_song_list:  # Ensure there are songs in the list
            QMessageBox.information(self.main_window, "Add songs to playlist", "Song list is empty")
            return

        # Add each song to the selected playlist
        for song in songs.current_song_list:
            add_song_to_database_table(song=song, table=playlist)

        self.load_playlists()

        print(f"Added {len(songs.current_song_list)} songs to playlist '{playlist}'.")  # Debug output


    # Add currently playing song to a playlist
    def add_currently_playing_to_a_playlist(self):
        if self.main_window.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            QMessageBox.information(self.main_window, "Add current song to playlist", "No song is playing in queue")
            return

        options = get_playlist_tables()  # Get available playlists
        if "favourites" in options:
            options.remove("favourites")  # Exclude favourites

        options.insert(0, "--Click to Select--")  # Default selection prompt

        # Prompt user to select a playlist
        playlist, ok = QInputDialog.getItem(
            self.main_window, "Add song to playlist",
            "Choose the desired playlist", options, editable=False)

        if not ok or playlist == "--Click to Select--":  # Validate selection
            QMessageBox.information(self.main_window, "Add song to playlist", "No playlist was selected.")
            return

        # Get currently playing media source
        current_media = self.main_window.player.source()
        song = current_media.toString().replace("file:///", "")  # Get file path correctly

        # Ensure the song path is valid before adding
        if not song.strip():
            QMessageBox.information(self.main_window, "Add song to playlist", "Error: No valid song found.")
            return

        add_song_to_database_table(song=song, table=playlist)  # Add song to database
        self.load_playlists()

        print(f"Added '{song}' to playlist '{playlist}'.")  # Debugging output


    # Load playlists songs to current list
    def load_playlist_songs_to_current_list(self, playlist):
        try:
            playlist_songs = fetch_all_songs_from_database_table(playlist)
            if len(playlist_songs) == 0:
                QMessageBox.information(self.main_window, "Load playlist song", "Playlist is empty")
                return

            # self.main_window.loaded_songs_listWidget.clear()
            for song in playlist_songs:
                songs.current_song_list.append(song)
                self.main_window.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon("images/MusicListItem.png"),
                        os.path.basename(song)))

        except Exception as e:
            print(f"Error loading songs from playlist '{playlist}': {e}")


    # Function to display the content of a selected playlist
    def show_playlist_content(self):
        try:
            playlist = self.main_window.playlists_listWidget.currentItem().text() # Get the name of the selected playlist from the UI list
            songs = fetch_all_songs_from_database_table(playlist)  # Retrieve all songs stored in the selected playlist from the database
            songs_only = [os.path.basename(song) for song in songs] # Extract only the song file names (excluding full paths)
            playlist_dialog = PlaylistDialog(songs_only, f'{playlist}') # Create and display a dialog window showing playlist contents
            playlist_dialog.exec()
        except Exception as e:
            print(f"Showing Playlist Content Error: {e}")
