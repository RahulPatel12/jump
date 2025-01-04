from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectLabel,
    DGG
)
from panda3d.core import TextNode

class PauseMenu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Semi-transparent background
        self.background = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-2, 2, -2, 2),
            pos=(0, 0, 0)
        )
        
        # Main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.4, 0.4, -0.5, 0.5),
            pos=(0, 0, 0),
            parent=self.background
        )
        
        # Title
        self.title = DirectLabel(
            text="Paused",
            text_scale=0.1,
            text_pos=(0, -0.03),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.35),
            parent=self.frame
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
        
        # Resume button
        self.resume_button = DirectButton(
            text="Resume",
            pos=(0, 0, 0.2),
            parent=self.frame,
            command=self.on_resume,
            **button_props
        )
        
        # Restart button
        self.restart_button = DirectButton(
            text="Restart Level",
            pos=(0, 0, 0.05),
            parent=self.frame,
            command=self.on_restart,
            **button_props
        )
        
        # Options button
        self.options_button = DirectButton(
            text="Options",
            pos=(0, 0, -0.1),
            parent=self.frame,
            command=self.on_options,
            **button_props
        )
        
        # Exit to menu button
        self.exit_button = DirectButton(
            text="Exit to Main Menu",
            pos=(0, 0, -0.25),
            parent=self.frame,
            command=self.on_exit_to_menu,
            **button_props
        )
        
        # Set up button hover effects
        for button in [self.resume_button, self.restart_button, 
                      self.options_button, self.exit_button]:
            button.bind(DGG.ENTER, self.on_button_hover, [button, True])
            button.bind(DGG.EXIT, self.on_button_hover, [button, False])
        
        # Show the menu
        self.show()
    
    def show(self):
        """Show the pause menu"""
        self.background.show()
        self.frame.show()
    
    def hide(self):
        """Hide the pause menu"""
        self.background.hide()
        self.frame.hide()
    
    def on_button_hover(self, button, hover, event):
        """Handle button hover effects"""
        if hover:
            button['frameColor'] = (0.3, 0.3, 0.3, 0.8)
        else:
            button['frameColor'] = (0.2, 0.2, 0.2, 0.8)
    
    def on_resume(self):
        """Handle resume button click"""
        self.hide()
        self.game_manager.request('Playing')
    
    def on_restart(self):
        """Handle restart button click"""
        self.hide()
        self.game_manager.request('Playing')  # Will restart the current level
    
    def on_options(self):
        """Handle options button click"""
        self.hide()
        self.game_manager.request('Options')
    
    def on_exit_to_menu(self):
        """Handle exit to menu button click"""
        self.hide()
        self.game_manager.request('MainMenu')
    
    def cleanup(self):
        """Clean up resources"""
        self.background.destroy()
        self.frame.destroy() 