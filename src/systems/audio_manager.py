from direct.showbase.Audio3DManager import Audio3DManager

class AudioManager:
    def __init__(self, base):
        self.base = base
        
        # Create audio managers
        self.audio3d = Audio3DManager(base.sfxManagerList[0])
        
        # Volume settings
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        
        # Currently playing music
        self.current_music = None
        
        # Sound cache
        self.sound_cache = {}
        
    def load_sound(self, sound_path):
        """Load a sound effect from file"""
        if sound_path not in self.sound_cache:
            self.sound_cache[sound_path] = self.base.loader.loadSfx(sound_path)
        return self.sound_cache[sound_path]
    
    def play_sound(self, sound_path, loop=False, volume=None):
        """Play a sound effect"""
        sound = self.load_sound(sound_path)
        if sound:
            sound.setLoop(loop)
            if volume is not None:
                sound.setVolume(volume * self.sfx_volume)
            else:
                sound.setVolume(self.sfx_volume)
            sound.play()
            return sound
        return None
    
    def play_3d_sound(self, sound_path, position, loop=False, volume=None):
        """Play a 3D positional sound effect"""
        sound = self.load_sound(sound_path)
        if sound:
            self.audio3d.attachSoundToObject(sound, position)
            sound.setLoop(loop)
            if volume is not None:
                sound.setVolume(volume * self.sfx_volume)
            else:
                sound.setVolume(self.sfx_volume)
            sound.play()
            return sound
        return None
    
    def play_music(self, music_path, loop=True):
        """Play background music"""
        if self.current_music:
            self.current_music.stop()
        
        self.current_music = self.load_sound(music_path)
        if self.current_music:
            self.current_music.setLoop(loop)
            self.current_music.setVolume(self.music_volume)
            self.current_music.play()
    
    def stop_music(self):
        """Stop currently playing music"""
        if self.current_music:
            self.current_music.stop()
            self.current_music = None
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music:
            self.current_music.setVolume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_music()
        for sound in self.sound_cache.values():
            sound.stop()
        self.sound_cache.clear() 