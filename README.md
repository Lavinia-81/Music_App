# Music_App

Advanced Python + PyQt6 Music Player  
A fully‑featured desktop music player built with *Python*, *PyQt6*, and *SQLite*, designed to manage playlists, favourites, and audio playback through a modern graphical interface.

This project was developed as the final presentation for my Python course and demonstrates real‑world GUI development, database integration, and multimedia handling.

---

## Overview
Music_App combines:
- a clean PyQt6 interface
- a robust audio engine powered by QMediaPlayer
- persistent storage using SQLite
- dynamic UI updates
- playlist and favorites management
- shuffle and loop playback modes

The application showcases how Python can be used to build interactive desktop software with real functionality and a polished user experience.

---

## Features
-  **Play, pause, and skip songs**
-  **Next/Previous Song**
-  **Manage playlists & favourites**
-  **Loop & shuffle modes**
-  **Interactive UI using PyQt6**
-  **Database storage for Favourites and Playlists**
-  **Dynamic UI Updates**: Update song information and playlist selections in real-time.

---

## Technical Details
- **Programming Language**: Python
- **GUI Framework**: PyQt6
- **Database**: SQLite (`app_db.db` is used to store playlists and songs)
- **Database Management**: **DB Browser for SQLite** (Used for editing and managing the database)
- **Core Components**:
  - `QMediaPlayer`: Handles audio playback.
  - `QListWidget`: Displays the playlist of songs.
  - Various buttons for functionalities like shuffle, loop, and navigation.
  - **SQLite Database (`app_db.db`)**: Stores playlists and favourite songs.
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
     python run.py
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


## Features
-  **Add songs to the favorites list**
-  **Delete individual songs or the entire favorites list**
-  **Automatically reload the list after modifications**
-  **Correct playback of selected songs**
-  **Save and manage the database using db_function.py**


## Installation & Setup

1. **Clone the project:**
   ```bash
   git clone https://github.com/username/MusicApp.git
   cd MusicApp
   ```
---

## Purpose of This Project
This application was created as my final Python course project, demonstrating:
- GUI development
- multimedia handling
- database integration
- event‑driven programming
- clean architecture

It remains an important milestone in my progression as a Python developer and is included in my portfolio to showcase practical, real‑world application development.

 ---
 
## Contribution
Contributions are welcome.
Feel free to fork the repository and submit a pull request with improvements or new features.
