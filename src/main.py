#!/usr/bin/env python3

import os
import sys

# Add src directory to Python path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import (
    WindowProperties, 
    TextNode, 
    loadPrcFileData,
    ConfigVariableString,
    ConfigVariableBool,
    ConfigVariableInt
)

# Configure Panda3D settings
loadPrcFileData("", """
    window-title Jump!
    win-size 1280 720
    framebuffer-multisample 1
    multisamples 2
    show-frame-rate-meter 1
    sync-video 1
    bullet-enable-contact-events #t
""")

from game.game_manager import GameManager
from systems.settings import Settings
from systems.input_manager import InputManager
from systems.audio_manager import AudioManager

class Jump(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class
        ShowBase.__init__(self)
        
        # Set window properties
        self.set_window_properties()
        
        # Initialize game systems
        self.settings = Settings()
        self.input_manager = InputManager()
        self.audio_manager = AudioManager(self)
        
        # Create game manager
        self.game_manager = GameManager(self)
        
        # Display loading screen
        self.show_loading_screen()
        
        # Start the game
        self.start_game()
    
    def set_window_properties(self):
        props = WindowProperties()
        props.setTitle("Jump!")
        props.setSize(1280, 720)  # Default resolution
        self.win.requestProperties(props)
    
    def show_loading_screen(self):
        # Create a simple loading text
        self.loading_text = OnscreenText(
            text="Loading...",
            pos=(0, 0),
            scale=0.1,
            align=TextNode.ACenter,
            mayChange=True
        )
    
    def start_game(self):
        # Remove loading screen
        self.loading_text.destroy()
        
        # Initialize game state
        self.game_manager.initialize()

def main():
    app = Jump()
    app.run()

if __name__ == "__main__":
    main() 