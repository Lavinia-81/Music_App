# Music_App

## Overview
**Music_App** is a music player application built using **Python** and **PyQt6**. It offers a user-friendly interface and a variety of features for managing and playing songs. The app leverages PyQt6 for its graphical user interface (GUI), including buttons and events that trigger core functionalities like looping songs, shuffling playlists, and navigating between tracks.

---

## Features
- ✅ **Play, pause, and skip songs**
- ✅ **Next/Previous Song**
- ✅ **Manage playlists & favorites**
- ✅ **Loop & shuffle modes**
- ✅ **Interactive UI using PyQt6**
- ✅ **Database storage for Favourites and Playlists**
- ✅ **Dynamic UI Updates**: Update song information and playlist selections in real-time.

---

## Technical Details
- **Programming Language**: Python
- **GUI Framework**: PyQt6
- **Database**: SQLite (`db.sqlite3` is used to store playlists and songs)
- **Database Management**: **DB Browser for SQLite** (Used for editing and managing the database)
- **Core Components**:
  - `QMediaPlayer`: Handles audio playback.
  - `QListWidget`: Displays the playlist of songs.
  - Various buttons for functionalities like shuffle, loop, and navigation.
  - **SQLite Database (`db.sqlite3`)**: Stores playlists and favorite songs.
  - **SQL Queries**: Used to manage song entries (e.g., INSERT, DELETE, UPDATE) within the database.
  
---

## Buttons and Their Events
Here’s a list of buttons in the application and their respective functionalities:
- **Loop Song Button (`loop_one_btn`)**:
  - Toggles looping for the currently playing song.
  - When enabled, prevents shuffling while maintaining the loop functionality.
- **Shuffle Playlist Button (`shuffle_song_btn`)**:
  - Enables or disables shuffling of the playlist.
  - Prevents looping while shuffle mode is active.
- **Next Song Button**:
  - Plays the next song in the playlist. Includes a loop-back mechanism for cyclic navigation.
- **Previous Song Button**:
  - Plays the previous song in the playlist.
- **Play/Pause Button**:
  - Starts or pauses the playback of the current song.

---

## How to Use
1. **Setup**:
   - Ensure Python is installed (recommended version: 3.9+).
   - Install PyQt6 using pip:
     ```bash
     pip install PyQt6
     ```

2. **Run the Application**:
   - Launch the app by executing the main script:
     ```bash
     python Music_App.py
     ```

3. **Using the Features**:
   - **Play a Song**: Select a song from the playlist and press the play button.
   - **Toggle Loop**: Click the "Loop Song" button to loop the current song.
   - **Enable Shuffle**: Click the "Shuffle Playlist" button for random playback.
   - **Navigate Tracks**: Use the "Next" and "Previous" buttons to move through the playlist.

---

## Error Handling
The application has built-in error handling to manage unexpected situations:
- **Looping Error**:
  - Displays a message when an error occurs during toggling the loop functionality.
- **Shuffle Error**:
  - Handles issues related to enabling or disabling shuffle mode.
- **Playback Navigation Error**:
  - Reports errors when navigating tracks (e.g., when a song index is out of bounds).


## 🚀 Features
- ✅ **Add songs to the favorites list**
- ❌ **Delete individual songs or the entire favorites list**
- 🔄 **Automatically reload the list after modifications**
- 🎧 **Correct playback of selected songs**
- 📁 **Save and manage the database using db_function.py**


# ⚙️ Installation & Setup

1. **Clone the project:**
   ```bash
   git clone https://github.com/username/MusicApp.git
   cd MusicApp
## Contribution
If you'd like to contribute to **Music_App**, feel free to fork this repository and submit a pull request. Suggestions for new features or bug fixes are always welcome!

---
