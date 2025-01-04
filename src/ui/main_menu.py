from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DGG
)
from panda3d.core import TextNode

class MainMenu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = DirectButton(
            text="Jump!",
            text_scale=0.15,
            text_pos=(0, -0.1),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.4),
            parent=self.frame,
            relief=None
        )
        
        # Create buttons
        button_props = {
            "frameSize": (-0.3, 0.3, -0.05, 0.05),
            "text_scale": 0.05,
            "text_pos": (0, -0.015),
            "text_fg": (1, 1, 1, 1),
            "text_align": TextNode.ACenter,
            "relief": DGG.FLAT,
            "frameColor": (0.2, 0.2, 0.2, 0.8),
            "pressEffect": True
        }
        
        # Play button
        self.play_button = DirectButton(
            text="Play",
            pos=(0, 0, 0.2),
            parent=self.frame,
            command=self.on_play,
            **button_props
        )
        
        # Options button
        self.options_button = DirectButton(
            text="Options",
            pos=(0, 0, 0.05),
            parent=self.frame,
            command=self.on_options,
            **button_props
        )
        
        # Leaderboard button
        self.leaderboard_button = DirectButton(
            text="Leaderboard",
            pos=(0, 0, -0.1),
            parent=self.frame,
            command=self.on_leaderboard,
            **button_props
        )
        
        # Exit button
        self.exit_button = DirectButton(
            text="Exit",
            pos=(0, 0, -0.25),
            parent=self.frame,
            command=self.on_exit,
            **button_props
        )
        
        # Set up button hover effects
        for button in [self.play_button, self.options_button, 
                      self.leaderboard_button, self.exit_button]:
            button.bind(DGG.ENTER, self.on_button_hover, [button, True])
            button.bind(DGG.EXIT, self.on_button_hover, [button, False])
        
        # Show the menu immediately
        self.show()
    
    def show(self):
        """Show the main menu"""
        self.frame.show()
    
    def hide(self):
        """Hide the main menu"""
        self.frame.hide()
    
    def on_button_hover(self, button, hover, event):
        """Handle button hover effects"""
        if hover:
            button['frameColor'] = (0.3, 0.3, 0.3, 0.8)
        else:
            button['frameColor'] = (0.2, 0.2, 0.2, 0.8)
    
    def on_play(self):
        """Handle play button click"""
        self.hide()
        self.game_manager.request('LevelSelect')
    
    def on_options(self):
        """Handle options button click"""
        self.hide()
        self.game_manager.request('Options')
    
    def on_leaderboard(self):
        """Handle leaderboard button click"""
        self.hide()
        self.game_manager.request('Leaderboard')
    
    def on_exit(self):
        """Handle exit button click"""
        self.base.userExit()
    
    def cleanup(self):
        """Clean up resources"""
        self.frame.destroy() 