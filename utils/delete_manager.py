from PyQt6.QtWidgets import QMessageBox
from db_functions import *


class DeleteManager:
    def __init__(self, main_window):
        self.main_window = main_window


    # Remove Selected Songs
    def remove_selected_song(self):
        try:
            if self.main_window.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self.main_window, 'Remove Selected Song',
                    'Playlist is empty'
                )
                return

            current_index = self.main_window.loaded_songs_listWidget.currentRow()
            if current_index is None or current_index < 0:
                QMessageBox.information(
                    self.main_window, 'Remove Selected Song',
                    'Select a song to remove'
                )
                return

            self.main_window.loaded_songs_listWidget.takeItem(current_index)
            if len(self.main_window.songs) > current_index:
                self.main_window.songs.pop(current_index)
            else:
                print("The list is empty or the index is invalid for pop.")

            print(f"Removed song at index {current_index}")

        except Exception as e:
            print(f"Remove selected song error: {e}")


    # Remove All Songs
    def remove_all_songs(self):
        try:
            if self.main_window.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self.main_window, 'Remove All Songs',
                    'The playlist is empty and there is nothing to remove.'
                )
                return

            question = QMessageBox.question(
                self.main_window, 'Remove All Songs',
                'This action will remove all songs from the list and cannot be undone.\n'
                'Do you want to continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if question == QMessageBox.StandardButton.Yes:
                self.main_window.stop_song()
                self.main_window.loaded_songs_listWidget.clear()
                self.main_window.songs.current_song_list.clear()

                print("All songs removed from the playlist.")

        except Exception as e:
            print(f"Error while removing all songs: {e}")


    # Remove Selected Playlist
    def remove_selected_playlist(self):
        try:
            selected_item = self.main_window.playlists_listWidget.currentItem()
            if not selected_item:
                QMessageBox.information(
                    self.main_window, 'Remove Selected Playlist',
                    'No playlist selected'
                )
                return

            playlist_name = selected_item.text()
            self.main_window.playlists_listWidget.takeItem(
                self.main_window.playlists_listWidget.currentRow()
            )

            print(f"Removed playlist: {playlist_name}")
            print(f"DEBUG: Trying to delete playlist = '{playlist_name}'")

        except Exception as e:
            print(f"Error removing selected playlist: {e}")


    # Remove All Playlist
    def remove_all_playlists(self):
        try:
            if self.main_window.playlists_listWidget.count() == 0:
                QMessageBox.information(
                    self.main_window, 'Remove All Playlists',
                    'There are no playlists to remove.'
                )
                return

            question = QMessageBox.question(
                self.main_window, 'Remove All Playlists',
                'This will delete all playlists and cannot be undone.\n'
                'Do you want to continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if question == QMessageBox.StandardButton.Yes:
                self.main_window.playlists_listWidget.clear()
                print("All playlists removed.")

        except Exception as e:
            print(f"Error while removing all playlists: {e}")


    # Delete Playlist
    def delete_playlist(self):
        try:
            selected_item = self.main_window.playlists_listWidget.currentItem()
            if selected_item is None:
                QMessageBox.information(self.main_window, "Delete Playlist", "No playlist selected.")
                return

            playlist = selected_item.text().strip() if selected_item and selected_item.text() else None
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

                if hasattr(self.main_window, "load_playlists"):
                    self.main_window.load_playlists()

                print(f"Deleted playlist '{playlist}' successfully!")

        except Exception as e:
            print(f"Error deleting playlist '{playlist}': {e}")
