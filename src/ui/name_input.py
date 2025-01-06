from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectEntry,
    DGG
)
from panda3d.core import TextNode

class NameInput:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = DirectButton(
            text="Enter Your Name",
            text_scale=0.08,
            text_pos=(0, -0.02),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.2),
            parent=self.frame,
            relief=None
        )
        
        # Name entry field
        self.name_entry = DirectEntry(
            text="",
            text_scale=0.05,
            frameSize=(-0.3, 0.3, -0.08, 0.08),
            frameColor=(0.15, 0.15, 0.15, 0.8),
            pos=(0, 0, 0),
            parent=self.frame,
            relief=DGG.FLAT,
            initialText="Player",
            numLines=1,
            focus=1,
            width=20,
            command=self.on_enter_press,
            text_fg=(1, 1, 1, 1),
            cursorKeys=1
        )
        
        # Continue button
        self.continue_button = DirectButton(
            text="Continue",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.2, 0.2, -0.05, 0.05),
            frameColor=(0.2, 0.6, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0, 0, -0.2),
            parent=self.frame,
            command=self.on_continue
        )
        
        # Back button
        self.back_button = DirectButton(
            text="Back",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.1, 0.1, -0.05, 0.05),
            frameColor=(0.6, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0, 0, -0.3),
            parent=self.frame,
            command=self.on_back
        )
        
        # Set up button hover effects
        for button in [self.continue_button, self.back_button]:
            button.bind(DGG.ENTER, self.on_button_hover, [button])
            button.bind(DGG.EXIT, self.on_button_exit, [button])
        
        # Show the menu
        self.show()
    
    def on_enter_press(self, text):
        """Handle enter key press in name entry"""
        self.on_continue()
    
    def on_continue(self):
        """Handle continue button click"""
        player_name = self.name_entry.get().strip()
        if player_name:  # Only proceed if name is not empty
            self.game_manager.player_name = player_name  # Store the name
            self.hide()
            self.game_manager.request('LevelSelect')
    
    def on_back(self):
        """Handle back button click"""
        self.hide()
        self.game_manager.request('MainMenu')
    
    def show(self):
        """Show the name input screen"""
        self.frame.show()
        # Focus the entry field
        self.name_entry.setFocus()
    
    def hide(self):
        """Hide the name input screen"""
        self.frame.hide()
    
    def on_button_hover(self, button, event):
        """Handle button hover effect"""
        orig_color = button['frameColor']
        button['frameColor'] = (
            min(orig_color[0] + 0.1, 1.0),
            min(orig_color[1] + 0.1, 1.0),
            min(orig_color[2] + 0.1, 1.0),
            orig_color[3]
        )
    
    def on_button_exit(self, button, event):
        """Handle button exit effect"""
        orig_color = button['frameColor']
        button['frameColor'] = (
            max(orig_color[0] - 0.1, 0.0),
            max(orig_color[1] - 0.1, 0.0),
            max(orig_color[2] - 0.1, 0.0),
            orig_color[3]
        )
    
    def cleanup(self):
        """Clean up resources"""
        self.frame.destroy() 