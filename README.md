# Python Music Player

A simple music player application built with Python, Tkinter, and Pygame.

## Features

*   Play local music files (.mp3).
*   Scan directories to build a music library.
*   Basic playback controls: Play, Pause, Stop, Next, Previous.
*   Volume control.
*   Save and Load playlists (in JSON format).
*   Search for tracks within the current playlist by filename.
*   Graphical User Interface using Tkinter.

## Prerequisites

*   Python 3 (should come with Tkinter)
*   Pygame library

## Setup and Installation

1.  **Clone the repository (if applicable) or download the source files.**

2.  **Install Pygame:**
    Open your terminal or command prompt and run:
    ```bash
    pip install pygame
    ```

## How to Run

1.  Navigate to the project's root directory in your terminal.
2.  Run the application using the following command:
    ```bash
    python main.py
    ```
3.  **Using the Player:**
    *   Click "Scan Folder" to select a directory containing your MP3 files.
    *   Once scanned, songs will appear in the listbox. Double-click a song to play it.
    *   Use the playback buttons (Play, Pause, etc.) to control music.
    *   Adjust volume using the slider.
    *   Use "Save Playlist" and "Load Playlist" to manage your playlists.
    *   Use the search bar to filter tracks in the current list.

## Project Structure

*   `main.py`: Main application script that launches the GUI.
*   `gui.py`: Contains the Tkinter GUI code (`MusicPlayerApp` class).
*   `playback/player.py`: Handles music playback logic using Pygame.
*   `library/scanner.py`: Handles scanning directories for music files.
*   `tests/`: Contains unit tests.
