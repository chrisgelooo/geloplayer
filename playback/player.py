import pygame

# Initialize pygame.mixer
pygame.mixer.init()

def load_track(filepath: str):
    """Loads a music file."""
    pygame.mixer.music.load(filepath)

def play_track():
    """Starts playback."""
    pygame.mixer.music.play()

def pause_track():
    """Pauses playback."""
    pygame.mixer.music.pause()

def unpause_track():
    """Resumes playback."""
    pygame.mixer.music.unpause()

def stop_track():
    """Stops playback."""
    pygame.mixer.music.stop()

def set_volume(volume_level: float):
    """Sets the volume for music playback.
    
    Args:
        volume_level: Float between 0.0 (mute) and 1.0 (max volume).
    """
    if 0.0 <= volume_level <= 1.0:
        pygame.mixer.music.set_volume(volume_level)
    elif volume_level < 0.0:
        pygame.mixer.music.set_volume(0.0)
    else:
        pygame.mixer.music.set_volume(1.0)

def get_volume() -> float:
    """Returns the current volume level (0.0 to 1.0)."""
    return pygame.mixer.music.get_volume()

def is_playing() -> bool:
    """
    Returns True if music is currently playing or paused (i.e., busy), 
    False otherwise.
    """
    return pygame.mixer.music.get_busy()
