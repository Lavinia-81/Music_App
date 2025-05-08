import os
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox
from PyQt6.QtGui import QIcon
from db_functions import fetch_all_songs_from_database_table, add_song_to_database_table, \
    delete_song_from_database_table, delete_all_songs_from_database_table
from utils import songs


class FavouritesManager:
    def __init__(self, main_window, songs_module):
        self.main_window = main_window
        self.songs = songs_module  # Ensure songs_module is passed correctly

        if not hasattr(self.songs, "favourites_song_list"):
            self.songs.favourites_song_list = []


    # FAVOURITE FUNCTIONS
    # Load Favourite song
    def load_favourites_into_app(self):
        try:
            favourite_songs = fetch_all_songs_from_database_table('favourites')

            print(f"Fetched favourites from DB: {favourite_songs}")

            self.main_window.favourites_listWidget.clear()
            songs.favourites_song_list.clear()
            print("Fetching songs from database:", favourite_songs)

            for favourite in favourite_songs:
                songs.favourites_song_list.append(favourite)

                self.main_window.favourites_listWidget.addItem(
                    QListWidgetItem(QIcon("utils/images/like.png"), os.path.basename(favourite)))

            print("Loaded favourites (AFTER ADDING):", songs.favourites_song_list)
        except Exception as e:
            print(f"Error loaded favourites: {e}")


    # Load All Favourites Songs
    def add_all_songs_to_favourites(self):
        if not self.songs.current_song_list:
            QMessageBox.information(self.main_window, 'Add songs to favourites', 'No songs have been loaded')
            return

        try:
            for song in self.songs.current_song_list:
                add_song_to_database_table(song, 'favourites')

            self.load_favourites_into_app()

            print(f"All songs added to favourites.")

        except Exception as e:
            print(f"Error adding songs to favourites: {e}")


    # Add Song to Favourites
    def add_song_to_favourites(self):
        current_index = self.main_window.loaded_songs_listWidget.currentRow()
        print(f"Selected index: {current_index}")
        print(f"Current song list: {self.songs.current_song_list}")

        if current_index < 0:
            QMessageBox.information(self.main_window,
                                    "Add Songs to Favourites",
                                    "Select a song to add to favourites")
            return

        try:
            song = self.songs.current_song_list[current_index]
            add_song_to_database_table(song=f"{song}", table='favourites')
            self.load_favourites_into_app()

            QMessageBox.information(self.main_window,
                                    "Add Songs to Favourites",
                                    f"{os.path.basename(song)} was successfully added to favourites.")
            return

        except Exception as e:
            print(f"Adding song to favourites error: {e}")


    # Remove Song From Favourites
    def remove_song_from_favourites(self):
        if self.main_window.favourites_listWidget.count() == 0:
            QMessageBox.information(self, 'Remove Song from Favourites', 'Favourites list is empty')
            return

        current_index = self.main_window.favourites_listWidget.currentRow()
        if current_index is None:  #== -1:
            QMessageBox.information(self, 'Remove Song from Favourites', 'Select a song to remove')
            return

        try:
            song_to_remove = songs.favourites_song_list[current_index]
            delete_song_from_database_table(song=song_to_remove, table='favourites')

            del songs.favourites_song_list[current_index]

            self.load_favourites_into_app()
            print(f"Successfully removed: {song_to_remove}")

        except Exception as e:
            print(f"Removing song error: {e}")


    # Remove All Songs From Favourites
    def remove_all_songs_from_favourites(self):
        if self.main_window.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self.main_window,
                "Remove Song from Favourites",
                "Favourites list is empty"
            )
            print("⚠ Favourites list is empty")
            return

        try:
            delete_all_songs_from_database_table(table="favourites")
            self.main_window.favourites_listWidget.clear()

            if hasattr(self, "load_favourites_into_app"):
                self.load_favourites_into_app()

            if self.main_window.favourites_listWidget.count() == 0:
                QMessageBox.information(
                    self.main_window,
                    "Favourites",
                    "No songs left in favourites!"
                )
                print("✅ All songs removed successfully!")

        except Exception as e:
            print(f"❌ Removing all songs error: {e}")

