import json
import os
from pathlib import Path

class Settings:
    def __init__(self):
        # Default settings
        self.default_settings = {
            "video": {
                "resolution": (1280, 720),
                "fullscreen": False,
                "vsync": True,
                "graphics_quality": "medium"  # low, medium, high
            },
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            },
            "controls": {
                "move_forward": ["w", "arrow_up"],
                "move_backward": ["s", "arrow_down"],
                "move_left": ["a", "arrow_left"],
                "move_right": ["d", "arrow_right"],
                "jump": ["space"],
                "run": ["shift"],
                "attack": ["mouse1"],
                "block": ["mouse2"],
                "dodge": ["control"],
                "pause": ["escape"],
                "interact": ["e"]
            }
        }
        
        self.settings = self.default_settings.copy()
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "settings.json"
        
        # Load settings from file if it exists
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings while preserving default values for missing keys
                    self._update_nested_dict(self.settings, loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _update_nested_dict(self, d, u):
        """Recursively update nested dictionary while preserving structure"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d:
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def get_setting(self, category, key):
        """Get a specific setting value"""
        try:
            return self.settings[category][key]
        except KeyError:
            return self.default_settings[category][key]
    
    def set_setting(self, category, key, value):
        """Set a specific setting value"""
        if category in self.settings and key in self.settings[category]:
            self.settings[category][key] = value
            self.save_settings()
    
    def reset_to_defaults(self, category=None):
        """Reset settings to defaults, optionally for a specific category"""
        if category:
            if category in self.settings:
                self.settings[category] = self.default_settings[category].copy()
        else:
            self.settings = self.default_settings.copy()
        self.save_settings()
    
    def get_resolution(self):
        """Get current resolution setting"""
        return self.get_setting("video", "resolution")
    
    def get_fullscreen(self):
        """Get fullscreen setting"""
        return self.get_setting("video", "fullscreen")
    
    def get_graphics_quality(self):
        """Get graphics quality setting"""
        return self.get_setting("video", "graphics_quality")
    
    def get_master_volume(self):
        """Get master volume setting"""
        return self.get_setting("audio", "master_volume")
    
    def get_music_volume(self):
        """Get music volume setting"""
        return self.get_setting("audio", "music_volume")
    
    def get_sfx_volume(self):
        """Get sound effects volume setting"""
        return self.get_setting("audio", "sfx_volume")
    
    def get_key_bindings(self):
        """Get all key bindings"""
        return self.get_setting("controls", {}) 