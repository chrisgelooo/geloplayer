import tkinter as tk
from tkinter import filedialog, Listbox, Scale, Scrollbar, Label, Button, messagebox, Entry
import pygame
import os
import json
from playback import player
from library import scanner

class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("500x500") # Adjusted height for search UI

        pygame.mixer.init()

        self.music_files = [] # Holds all tracks from scan/load
        self.displayed_music_files = [] # Holds tracks currently shown in listbox (all or search results)
        self.selected_track_path = None
        self.current_track_index = -1 

        self.initial_volume = 0.5
        player.set_volume(self.initial_volume)
        self.is_paused_flag = False

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Song Title Label
        self.song_title_label = Label(self.root, text="No track selected", font=("Arial", 12))
        self.song_title_label.pack(pady=5)

        # Search Frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5, padx=10, fill=tk.X)

        self.search_entry = Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=0, padx=(0,5), sticky="ew")
        
        self.search_button = Button(search_frame, text="Search", command=self.search_tracks)
        self.search_button.grid(row=0, column=1, padx=5)

        self.clear_search_button = Button(search_frame, text="Clear", command=self.clear_search)
        self.clear_search_button.grid(row=0, column=2, padx=5)
        search_frame.grid_columnconfigure(0, weight=1) # Allow entry to expand


        # Playlist/Library Listbox with Scrollbar
        playlist_frame = tk.Frame(self.root)
        playlist_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.playlist_listbox = Listbox(playlist_frame, selectmode=tk.SINGLE, exportselection=False)
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = Scrollbar(playlist_frame, orient=tk.VERTICAL, command=self.playlist_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_listbox.config(yscrollcommand=scrollbar.set)
        self.playlist_listbox.bind("<Double-1>", self.play_selected_from_listbox)

        # Controls Frame
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=5)

        self.prev_button = Button(controls_frame, text="Previous", command=self.prev_song)
        self.prev_button.grid(row=0, column=0, padx=5)
        self.play_button = Button(controls_frame, text="Play", command=self.play_song)
        self.play_button.grid(row=0, column=1, padx=5)
        self.pause_button = Button(controls_frame, text="Pause/Unpause", command=self.pause_song)
        self.pause_button.grid(row=0, column=2, padx=5)
        self.stop_button = Button(controls_frame, text="Stop", command=self.stop_song)
        self.stop_button.grid(row=0, column=3, padx=5)
        self.next_button = Button(controls_frame, text="Next", command=self.next_song)
        self.next_button.grid(row=0, column=4, padx=5)

        # Volume Slider
        self.volume_scale = Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, 
                                  label="Volume", command=self.adjust_volume, length=200)
        self.volume_scale.set(self.initial_volume * 100)
        self.volume_scale.pack(pady=5)

        # File Operations Frame
        file_ops_frame = tk.Frame(self.root)
        file_ops_frame.pack(pady=5)
        self.scan_button = Button(file_ops_frame, text="Scan Folder", command=self.scan_folder)
        self.scan_button.grid(row=0, column=0, padx=5)
        self.save_playlist_button = Button(file_ops_frame, text="Save Playlist", command=self.save_playlist)
        self.save_playlist_button.grid(row=0, column=1, padx=5)
        self.load_playlist_button = Button(file_ops_frame, text="Load Playlist", command=self.load_playlist)
        self.load_playlist_button.grid(row=0, column=2, padx=5)

    def search_tracks(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.clear_search()
            return

        if not self.music_files:
            messagebox.showinfo("Search", "No tracks loaded to search.")
            return

        self.displayed_music_files = [
            f for f in self.music_files if query in os.path.basename(f).lower()
        ]
        
        self.selected_track_path = None
        self.current_track_index = -1
        self.populate_playlist_listbox()
        self.update_song_title() # Update to "No track selected" or similar
        if not self.displayed_music_files:
            messagebox.showinfo("Search", f"No tracks found matching '{query}'.")


    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.displayed_music_files = list(self.music_files) # Show all original tracks
        
        self.selected_track_path = None
        self.current_track_index = -1
        self.populate_playlist_listbox()
        self.update_song_title()


    def update_song_title(self, title_path=None):
        if title_path:
            base_title = os.path.basename(title_path)
            current_status = ""
            if self.is_paused_flag:
                 current_status = "Paused: "
            elif player.is_playing(): # Check if pygame mixer is actively playing
                 # Need to be careful: get_busy() is true if paused OR playing.
                 # A more reliable check for "playing" might be pygame.mixer.music.get_busy() and not self.is_paused_flag
                 if pygame.mixer.music.get_busy() and not self.is_paused_flag:
                    current_status = "Playing: "
                 else: # If it's busy but we think it's paused, or not busy at all
                    current_status = "Loaded: " # Or "Stopped: " if appropriate
            else: # Not playing, not paused.
                 current_status = "Loaded: "
            if title_path.endswith("(Stopped)"): # Special case from stop_song
                current_status = "" # Remove prefix if already indicating stopped

            self.song_title_label.config(text=f"{current_status}{base_title}")
        else:
            self.song_title_label.config(text="No track selected")


    def populate_playlist_listbox(self):
        self.playlist_listbox.delete(0, tk.END) 
        for i, file_path in enumerate(self.displayed_music_files): # Use displayed_music_files
            self.playlist_listbox.insert(tk.END, f"{i+1}. {os.path.basename(file_path)}")
        
        if self.current_track_index != -1 and self.current_track_index < len(self.displayed_music_files):
            self.playlist_listbox.selection_set(self.current_track_index)
            self.playlist_listbox.activate(self.current_track_index)
            self.playlist_listbox.see(self.current_track_index)
        else:
            self.playlist_listbox.selection_clear(0, tk.END)


    def play_selected_from_listbox(self, event=None):
        selected_indices = self.playlist_listbox.curselection()
        if not selected_indices:
            return
        
        self.current_track_index = selected_indices[0]
        # Important: get path from displayed_music_files
        self.selected_track_path = self.displayed_music_files[self.current_track_index]
        
        try:
            player.load_track(self.selected_track_path)
            player.play_track()
            self.is_paused_flag = False
            self.update_song_title(self.selected_track_path)
        except pygame.error as e:
            messagebox.showerror("Playback Error", f"Error playing selected track: {e}\nThe file might be corrupted or not a valid audio format.")
            self.update_song_title("Error loading track") # Generic error for title
            self.selected_track_path = None
            self.current_track_index = -1

    def play_song(self):
        if not self.selected_track_path: # If no specific track is selected (e.g. after stop or launch)
            if self.displayed_music_files: # Check if there are any tracks in the listbox
                if self.current_track_index == -1 : # If no track was ever selected from current list, pick first
                     self.current_track_index = 0
                
                # Ensure current_track_index is valid for displayed_music_files
                if 0 <= self.current_track_index < len(self.displayed_music_files):
                    self.selected_track_path = self.displayed_music_files[self.current_track_index]
                else: # Fallback to first track if index is somehow out of sync
                    self.current_track_index = 0
                    self.selected_track_path = self.displayed_music_files[self.current_track_index]

                try:
                    player.load_track(self.selected_track_path)
                    self.playlist_listbox.selection_clear(0, tk.END)
                    self.playlist_listbox.selection_set(self.current_track_index)
                    self.playlist_listbox.activate(self.current_track_index)
                except pygame.error as e:
                    messagebox.showerror("Playback Error", f"Error loading track: {e}")
                    self.update_song_title("Error loading track")
                    self.selected_track_path = None
                    self.current_track_index = -1
                    return
            else:
                messagebox.showinfo("Playback Info", "No tracks available to play. Scan a folder or load a playlist.")
                self.update_song_title("No track to play")
                return
        
        # If selected_track_path is already set, just play (or resume if paused)
        player.play_track() # Pygame's play handles playing from start or unpausing.
        self.is_paused_flag = False
        self.update_song_title(self.selected_track_path)


    def pause_song(self):
        if self.selected_track_path and pygame.mixer.music.get_busy(): # Only act if a song is loaded and playing/paused
            if not self.is_paused_flag: 
                player.pause_track()
                self.is_paused_flag = True
            else: 
                player.unpause_track()
                self.is_paused_flag = False
            self.update_song_title(self.selected_track_path)
        elif not self.selected_track_path:
            messagebox.showinfo("Playback Info", "No track loaded to pause/unpause.")
        # If not busy (i.e. stopped), do nothing for pause button

    def stop_song(self):
        if self.selected_track_path: 
            player.stop_track()
            self.is_paused_flag = False
            self.update_song_title(self.selected_track_path + " (Stopped)")
        else:
            messagebox.showinfo("Playback Info", "No track loaded to stop.")


    def next_song(self):
        if not self.displayed_music_files:
            messagebox.showinfo("Playlist Info", "Playlist is empty.")
            return

        if self.current_track_index < len(self.displayed_music_files) - 1:
            self.current_track_index += 1
        else:
            self.current_track_index = 0 

        self.selected_track_path = self.displayed_music_files[self.current_track_index]
        try:
            player.load_track(self.selected_track_path)
            player.play_track()
            self.is_paused_flag = False
            self.update_song_title(self.selected_track_path)
            self.playlist_listbox.selection_clear(0, tk.END)
            self.playlist_listbox.selection_set(self.current_track_index)
            self.playlist_listbox.activate(self.current_track_index)
        except pygame.error as e:
            messagebox.showerror("Playback Error", f"Error loading next track: {e}")
            self.update_song_title("Error loading track")
            self.selected_track_path = None 
            self.current_track_index = -1

    def prev_song(self):
        if not self.displayed_music_files:
            messagebox.showinfo("Playlist Info", "Playlist is empty.")
            return

        if self.current_track_index > 0:
            self.current_track_index -= 1
        else:
            self.current_track_index = len(self.displayed_music_files) - 1 

        self.selected_track_path = self.displayed_music_files[self.current_track_index]
        try:
            player.load_track(self.selected_track_path)
            player.play_track()
            self.is_paused_flag = False
            self.update_song_title(self.selected_track_path)
            self.playlist_listbox.selection_clear(0, tk.END)
            self.playlist_listbox.selection_set(self.current_track_index)
            self.playlist_listbox.activate(self.current_track_index)
        except pygame.error as e:
            messagebox.showerror("Playback Error", f"Error loading previous track: {e}")
            self.update_song_title("Error loading track")
            self.selected_track_path = None 
            self.current_track_index = -1

    def adjust_volume(self, volume_str):
        volume_level = float(volume_str) / 100.0
        player.set_volume(volume_level)

    def scan_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            if player.is_playing() or self.is_paused_flag:
                player.stop_track()
                self.is_paused_flag = False
            
            self.music_files = scanner.scan_directory(directory)
            self.clear_search() # This will set displayed_music_files and update UI
            # clear_search already calls populate_playlist_listbox and update_song_title
            
            if self.music_files:
                messagebox.showinfo("Scan Complete", f"Found {len(self.music_files)} MP3 tracks in '{directory}'.")
            else:
                messagebox.showinfo("Scan Complete", f"No .mp3 files found in '{directory}'.")

    def save_playlist(self):
        if not self.music_files: # Save original full list, not potentially filtered one
            messagebox.showinfo("Save Playlist", "Main playlist is empty. Nothing to save.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.music_files, f, indent=4) # Save original list
                messagebox.showinfo("Save Playlist", "Playlist saved successfully.")
            except Exception as e:
                messagebox.showerror("Save Playlist Error", f"Error saving playlist: {e}")

    def load_playlist(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    loaded_data = json.load(f)
                
                if not isinstance(loaded_data, list) or not all(isinstance(item, str) for item in loaded_data):
                    raise ValueError("Playlist file is not a valid list of track paths.")

                if player.is_playing() or self.is_paused_flag:
                    player.stop_track()
                    self.is_paused_flag = False

                self.music_files = loaded_data
                self.clear_search() # This will set displayed_music_files and update UI

                if self.music_files:
                    messagebox.showinfo("Load Playlist", "Playlist loaded successfully.")
                else:
                    messagebox.showinfo("Load Playlist", "Loaded playlist is empty.")
            
            except FileNotFoundError:
                messagebox.showerror("Load Playlist Error", "File not found.")
            except json.JSONDecodeError:
                messagebox.showerror("Load Playlist Error", "Invalid JSON format in playlist file.")
            except ValueError as ve:
                messagebox.showerror("Load Playlist Error", f"Error in playlist data: {ve}")
            except Exception as e:
                messagebox.showerror("Load Playlist Error", f"An unexpected error occurred: {e}")

    def on_closing(self):
        if player.is_playing() or self.is_paused_flag: # Check both states
            player.stop_track()
        pygame.mixer.quit()
        self.root.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = MusicPlayerApp(root)
#     root.mainloop()
