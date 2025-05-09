from PyQt6.QtWidgets import QListWidgetItem, QMessageBox, QInputDialog
from PyQt6.QtGui import QIcon
import os.path
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
            existing = get_playlist_tables()
            name, ok = QInputDialog.getText(self.main_window, "Create new playlist", "Enter playlist name")

            if not ok or not name.strip() or any(c in name for c in r'\/:*?"<>|'):
                QMessageBox.information(self.main_window, "Name Error", "Invalid playlist name.")
                return

            if name not in existing:
                create_database_or_database_table(name)
                self.load_playlists()
                print(f"Playlist '{name}' created successfully.")
            else:
                caution = QMessageBox.question(
                    self.main_window, "Replace Playlist",
                    f"A playlist with name '{name}' already exists.\nDo you want to continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if caution == QMessageBox.StandardButton.Yes:
                    delete_database_table(name)
                    create_database_or_database_table(name)
                    self.load_playlists()
                    print(f"Playlist '{name}' replaced successfully.")

        except Exception as e:
            print(f"Error creating new playlist: {e}")


    # Delete a playlist
    def delete_playlist(self):
        try:
            selected_item = self.main_window.playlists_listWidget.currentItem()
            if selected_item is None:
                QMessageBox.information(self.main_window, "Delete Playlist", "No playlist selected.")
                return

            playlist = selected_item.text().strip()

            if not playlist:
                QMessageBox.information(self.main_window, "Delete Playlist", "Invalid playlist name.")
                return

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
            print(f"Error deleting playlist '{playlist}': {e}")


    # Delete all playlists
    def delete_all_playlists(self):
        try:
            playlists = get_playlist_tables()
            if "favourites" in playlists:
                playlists.remove("favourites")

            caution = QMessageBox.question(
                self.main_window, "Delete all Playlists",
                "This action will delete all playlists and it cannot be reversed.\nDo you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if caution == QMessageBox.StandardButton.Yes:
                for playlist in playlists:
                    delete_database_table(playlist)

                self.load_playlists()

                print("All playlists (except favourites) have been deleted.")
        except Exception as e:
            print(f"Error deleting all playlists: {e}")


    # Add song to playlist
    def add_a_song_to_a_playlist(self):
        try:
            options = get_playlist_tables()
            if "favourites" in options:
                options.remove("favourites")

            options.insert(0, "--Click to Select--")
            playlist, ok = QInputDialog.getItem(self, "Add song to playlist", "Choose the desired playlist", options,
                                                editable=False)

            if not ok or playlist == "--Click to Select--":
                QMessageBox.information(self, "Add song to playlist", "No playlist was selected.")
                return

            song_list = songs.current_song_list
            list_widget = self.main_window.loaded_songs_listWidget

            if self.main_window.stackedWidget.currentIndex() == 2:
                song_list = songs.favourites_song_list
                list_widget = self.main_window.favourites_listWidget

            if not song_list:
                QMessageBox.information(self, "Unsuccessful", "No songs available.")
                return

            current_index = list_widget.currentRow()
            if current_index == -1 or current_index >= len(song_list):
                QMessageBox.information(self, "Unsuccessful", "No song selected.")
                return

            song = song_list[current_index]

            if not song or song.strip() == "":
                print("Error: Song name is empty!")
                return

            add_song_to_database_table(song=song, table=playlist)
            self.load_playlists()

            print(f"Added '{song}' to playlist '{playlist}'.")

        except Exception as e:
            print(f"Error adding song to playlist '{playlist}': {e}")


    # Add all current songs to a playlist
    def add_all_current_songs_to_a_playlist(self):
        try:
            options = get_playlist_tables()
            if "favourites" in options:
                options.remove("favourites")
            options.insert(0, "--Click to Select--")
            playlist, ok = QInputDialog.getItem(self.main_window, "Add song to playlist", "Choose the desired playlist", options, editable=False)
            if not ok or playlist == "--Click to Select--":
                QMessageBox.information(self.main_window, "Add song to playlist", "No playlist was selected")
                return

            if not songs.current_song_list:
                QMessageBox.information(self.main_window, "Add songs to playlist", "Song list is empty")
                return

            for song in songs.current_song_list:
                if not song or song.strip() == "":
                    print("Error: Song name is empty!")
                    continue

                add_song_to_database_table(song=song, table=playlist)

            self.load_playlists()
            print(f"Added {len(songs.current_song_list)} songs to playlist '{playlist}'.")

        except Exception as e:
            print(f"Error adding songs to playlist '{playlist}': {e}")


    # Load playlists songs to current list
    def load_playlist_songs_to_current_list(self, playlist):
        try:
            playlist_songs = fetch_all_songs_from_database_table(playlist)
            if not playlist_songs:
                QMessageBox.information(self.main_window, "Load playlist song", "Playlist is empty")
                return

            self.main_window.loaded_songs_listWidget.clear()
            for song in playlist_songs:
                if not song or song.strip() == "":
                    continue

                item = QListWidgetItem(QIcon("images/MusicListItem.png"), os.path.basename(song))
                self.main_window.loaded_songs_listWidget.addItem(item)

            # print(f"Loaded {len(playlist_songs)} songs from playlist '{playlist}'.")

        except Exception as e:
            print(f"Error loading songs from playlist '{playlist}': {e}")


    # Show Playlist Content
    def show_playlist_content(self):
        try:
            playlist = self.main_window.playlists_listWidget.currentItem().text()
            songs = fetch_all_songs_from_database_table(playlist)
            songs_only = [os.path.basename(song[0]) for song in songs]
            playlist_dialog = PlaylistDialog(songs_only, f'{playlist}')
            playlist_dialog.exec()

        except Exception as e:
            print(f"Showing Playlist Content Error: {e}")
