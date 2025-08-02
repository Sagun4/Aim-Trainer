import pygame
import os
from enum import Enum
from typing import Dict, Optional

class SoundEffect(Enum):
    HIT = "hit"
    MISS = "miss"
    TARGET_SPAWN = "spawn"
    ACHIEVEMENT = "achievement"
    MENU_CLICK = "menu_click"
    GAME_START = "game_start"
    GAME_END = "game_end"
    STREAK = "streak"
    BONUS_HIT = "bonus_hit"

class SoundManager:
    """Manages all game audio with volume control and audio pooling"""
    
    def __init__(self, sounds_folder: str = "sounds"):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.sounds_folder = sounds_folder
        self.sounds: Dict[SoundEffect, pygame.mixer.Sound] = {}
        self.volume = 0.7
        self.enabled = True
        
        # Create sounds folder if it doesn't exist
        os.makedirs(sounds_folder, exist_ok=True)
        
        # Load or create default sounds
        self._load_sounds()
        
        # Background music
        self.music_volume = 0.3
        self.current_music = None
    
    def _load_sounds(self):
        """Load sound files or create placeholder sounds"""
        sound_files = {
            SoundEffect.HIT: "hit.wav",
            SoundEffect.MISS: "miss.wav",
            SoundEffect.TARGET_SPAWN: "spawn.wav",
            SoundEffect.ACHIEVEMENT: "achievement.wav",
            SoundEffect.MENU_CLICK: "click.wav",
            SoundEffect.GAME_START: "start.wav",
            SoundEffect.GAME_END: "end.wav",
            SoundEffect.STREAK: "streak.wav",
            SoundEffect.BONUS_HIT: "bonus.wav"
        }
        
        for effect, filename in sound_files.items():
            filepath = os.path.join(self.sounds_folder, filename)
            
            if os.path.exists(filepath):
                try:
                    self.sounds[effect] = pygame.mixer.Sound(filepath)
                except pygame.error:
                    self.sounds[effect] = self._create_placeholder_sound(effect)
            else:
                self.sounds[effect] = self._create_placeholder_sound(effect)
    
    def _create_placeholder_sound(self, effect: SoundEffect) -> pygame.mixer.Sound:
        """Create procedural sounds when audio files are missing"""
        import numpy as np
        
        sample_rate = 22050
        
        if effect == SoundEffect.HIT:
            # Short, high-pitched ping
            duration = 0.1
            frequency = 800
        elif effect == SoundEffect.MISS:
            # Lower, duller thud
            duration = 0.15
            frequency = 200
        elif effect == SoundEffect.ACHIEVEMENT:
            # Triumphant chord progression
            duration = 0.5
            frequency = 440
        elif effect == SoundEffect.STREAK:
            # Rising pitch
            duration = 0.3
            frequency = 600
        else:
            # Default click sound
            duration = 0.05
            frequency = 1000
        
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # Generate sine wave with envelope
        for i in range(frames):
            time_point = i / sample_rate
            envelope = max(0, 1 - time_point / duration)  # Linear decay
            
            if effect == SoundEffect.STREAK:
                # Rising frequency for streak
                current_freq = frequency * (1 + time_point * 2)
            else:
                current_freq = frequency
            
            wave = np.sin(2 * np.pi * current_freq * time_point) * envelope * 0.3
            arr[i] = [wave, wave]
        
        # Convert to pygame sound
        sound_array = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(sound_array)
    
    def play(self, effect: SoundEffect, volume_multiplier: float = 1.0):
        """Play a sound effect"""
        if not self.enabled or effect not in self.sounds:
            return
        
        sound = self.sounds[effect]
        sound.set_volume(self.volume * volume_multiplier)
        sound.play()
    
    def play_music(self, music_file: str, loops: int = -1):
        """Play background music"""
        if not self.enabled:
            return
        
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
            self.current_music = music_file
        except pygame.error:
            pass  # Music file not found or invalid
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_enabled(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()
    
    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.quit()
