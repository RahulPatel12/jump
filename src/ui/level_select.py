from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectScrolledFrame,
    DGG
)
from panda3d.core import TextNode

class LevelSelect:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = DirectButton(
            text="Select Level",
            text_scale=0.1,
            text_pos=(0, -0.03),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.6),
            parent=self.frame,
            relief=None
        )
        
        # Create scrolled frame for level list
        self.level_frame = DirectScrolledFrame(
            frameSize=(-0.4, 0.4, -0.5, 0.5),
            canvasSize=(-0.35, 0.35, -1, 1),  # Will be adjusted based on number of levels
            frameColor=(0.15, 0.15, 0.15, 0.8),
            scrollBarWidth=0.04,
            parent=self.frame,
            pos=(-0.3, 0, 0)
        )
        
        # Level preview frame
        self.preview_frame = DirectFrame(
            frameSize=(-0.3, 0.3, -0.3, 0.3),
            frameColor=(0.2, 0.2, 0.2, 0.8),
            pos=(0.4, 0, 0.1),
            parent=self.frame
        )
        
        # Level info text
        self.level_info = DirectButton(
            text="",
            text_scale=0.05,
            text_pos=(0, -0.02),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0.4, 0, -0.3),
            parent=self.frame,
            relief=None
        )
        
        # Start level button
        self.start_button = DirectButton(
            text="Start Level",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.2, 0.2, -0.05, 0.05),
            frameColor=(0.2, 0.6, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0.4, 0, -0.5),
            parent=self.frame,
            command=self.on_start_level
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
            pos=(-0.6, 0, -0.7),
            parent=self.frame,
            command=self.on_back
        )
        
        # Currently selected level
        self.selected_level = None
        
        # Create level buttons
        self.level_buttons = []
        self.create_level_buttons()
        
        # Set up button hover effects
        for button in [self.start_button, self.back_button]:
            button.bind(DGG.ENTER, self.on_button_hover, [button])
            button.bind(DGG.EXIT, self.on_button_exit, [button])
        
        # Show the menu
        self.show()
    
    def create_level_buttons(self):
        """Create buttons for each available level"""
        # For now, just create a single test level
        button = DirectButton(
            text="Level 1",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.3, 0.3, -0.05, 0.05),
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0, 0, 0.3),
            parent=self.level_frame.getCanvas(),
            command=self.on_level_select,
            extraArgs=[{
                'name': 'Level 1',
                'description': 'A simple test level to get started.\nCollect coins and reach the goal!'
            }]
        )
        button.bind(DGG.ENTER, self.on_button_hover, [button])
        button.bind(DGG.EXIT, self.on_button_exit, [button])
        self.level_buttons.append(button)
    
    def on_level_select(self, level_data):
        """Handle level selection"""
        self.selected_level = level_data
        self.level_info["text"] = f"{level_data['name']}\n\n{level_data['description']}"
        # TODO: Update preview image
    
    def on_start_level(self):
        """Handle start level button click"""
        if self.selected_level:
            self.hide()
            self.game_manager.request('Playing', self.selected_level['name'])
    
    def on_back(self):
        """Handle back button click"""
        self.hide()
        self.game_manager.request('MainMenu')
    
    def show(self):
        """Show the level selection screen"""
        self.frame.show()
    
    def hide(self):
        """Hide the level selection screen"""
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