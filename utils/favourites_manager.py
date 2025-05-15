import os
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox
from PyQt6.QtGui import QIcon
from db_functions import fetch_all_songs_from_database_table, add_song_to_database_table, \
    delete_song_from_database_table, delete_all_songs_from_database_table
from utils import songs


class FavouritesManager:
    def __init__(self, main_window, songs_module):
        self.main_window = main_window
        self.songs = songs_module  # Store reference to song management module

        # Ensure that favourites_song_list exists in songs_module
        if not hasattr(self.songs, "favourites_song_list"):
            self.songs.favourites_song_list = []


    # FAVOURITE FUNCTIONS
    # Load Favourite song
    def load_favourites_into_app(self):
        try:
            favourite_songs = fetch_all_songs_from_database_table('favourites')

            # print(f"Fetched favourites from DB: {favourite_songs}")

            self.main_window.favourites_listWidget.clear() # Clear UI list
            songs.favourites_song_list.clear() # Clear local favourites list
            # print("Fetching songs from database:", favourite_songs)

            # Add retrieved favourite songs to UI list
            for favourite in favourite_songs:
                songs.favourites_song_list.append(favourite)

                self.main_window.favourites_listWidget.addItem(
                    QListWidgetItem(QIcon("utils/images/like.png"), os.path.basename(favourite)))

            # print("Loaded favourites (AFTER ADDING):", songs.favourites_song_list)
        except Exception as e:
            print(f"Error loaded favourites: {e}")


    # Load All Favourites Songs
    def add_all_songs_to_favourites(self):
        if not self.songs.current_song_list: # Ensure there are songs to add
            QMessageBox.information(self.main_window,
                                    'Add songs to favourites',
                                    'No songs have been loaded')
            return

        try:
            # Add each song to the favourites database
            for song in self.songs.current_song_list:
                add_song_to_database_table(song, 'favourites')

            self.load_favourites_into_app() # Reload favourites into the UI

            print(f"All songs added to favourites.")

        except Exception as e:
            print(f"Error adding songs to favourites: {e}")


    # Add a selected song to favourites
    def add_song_to_favourites(self):
        current_index = self.main_window.loaded_songs_listWidget.currentRow()
        print(f"Selected index: {current_index}")
        # print(f"Current song list: {self.songs.current_song_list}")

        if current_index < 0: # Ensure a song is selected
            QMessageBox.information(self.main_window,
                                    "Add Songs to Favourites",
                                    "Select a song to add to favourites")
            return

        try:
            song = self.songs.current_song_list[current_index] # Get selected song
            add_song_to_database_table(song=f"{song}", table='favourites')  # Add song to favourites DB
            self.load_favourites_into_app() # Reload UI

            QMessageBox.information(self.main_window,
                                    "Add Songs to Favourites",
                                    f"{os.path.basename(song)} was successfully added to favourites.")
            return

        except Exception as e:
            print(f"Adding song to favourites error: {e}")


    # Remove a selected song from favourites
    def remove_song_from_favourites(self):
        if self.main_window.favourites_listWidget.count() == 0: # Ensure there are favourites to remove
            QMessageBox.information(self.main_window, 'Remove Song from Favourites', 'Favourites list is empty')
            return

        current_index = self.main_window.favourites_listWidget.currentRow() # Get selected song index
        if current_index is None:  #== -1:
            QMessageBox.information(self.main_window, 'Remove Song from Favourites', 'Select a song to remove')
            return

        try:
            song_to_remove = songs.favourites_song_list[current_index] # Get song to be removed
            delete_song_from_database_table(song=song_to_remove, table='favourites') # Remove song from DB

            del songs.favourites_song_list[current_index] # Remove song from local favourites list

            self.load_favourites_into_app() # Reload UI
            print(f"Successfully removed: {song_to_remove}")

        except Exception as e:
            print(f"Removing song error: {e}")


    # Remove All Songs From Favourites
    def remove_all_songs_from_favourites(self):
        if self.main_window.favourites_listWidget.count() == 0: # Ensure there are favourites to remove
            QMessageBox.information(
                self.main_window,
                "Remove Song from Favourites",
                "Favourites list is empty"
            )
            print("Favourites list is empty")
            return

        try:
            delete_all_songs_from_database_table(table="favourites") # Remove all songs from DB
            self.main_window.favourites_listWidget.clear() # Clear UI list

            if hasattr(self, "load_favourites_into_app"): # Reload favourites if applicable
                self.load_favourites_into_app()

            if self.main_window.favourites_listWidget.count() == 0:  # Confirm removal if the UI list is empty
                QMessageBox.information(
                    self.main_window,
                    "Favourites",
                    "No songs left in favourites!"
                )
                print("All songs removed successfully!")

        except Exception as e:
            print(f"Removing all songs error: {e}")
