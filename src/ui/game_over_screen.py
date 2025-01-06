from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DGG
from panda3d.core import TextNode

class GameOverScreen:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create semi-transparent background
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-2, 2, -2, 2),
            pos=(0, 0, 0)
        )
        
        # Create game over text
        self.game_over_text = DirectLabel(
            text="Game Over",
            text_scale=0.15,
            text_fg=(1, 0, 0, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.2),
            parent=self.frame
        )
        
        # Create score display
        if hasattr(game_manager, 'current_score'):
            score_text = f"Final Score: {game_manager.current_score}"
        else:
            score_text = "Final Score: 0"
        
        self.final_score_text = DirectLabel(
            text=score_text,
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0),
            parent=self.frame
        )
        
        # Create buttons
        button_props = {
            "frameSize": (-0.2, 0.2, -0.05, 0.05),
            "text_scale": 0.05,
            "text_pos": (0, -0.015),
            "text_fg": (1, 1, 1, 1),
            "text_align": TextNode.ACenter,
            "relief": DGG.FLAT,
            "frameColor": (0.2, 0.2, 0.2, 0.8),
            "pressEffect": True
        }
        
        # Retry button
        self.retry_button = DirectButton(
            text="Retry Level",
            pos=(0, 0, -0.2),
            command=self.on_retry,
            parent=self.frame,
            **button_props
        )
        
        # Main menu button
        self.menu_button = DirectButton(
            text="Main Menu",
            pos=(0, 0, -0.3),
            command=self.on_menu,
            parent=self.frame,
            **button_props
        )
        
        # Set up button hover effects
        for button in [self.retry_button, self.menu_button]:
            button.bind(DGG.ENTER, self.on_button_hover, [button, True])
            button.bind(DGG.EXIT, self.on_button_hover, [button, False])
    
    def on_retry(self):
        """Handle retry button click"""
        self.game_manager.request('Playing')
    
    def on_menu(self):
        """Handle menu button click"""
        self.game_manager.request('MainMenu')
    
    def on_button_hover(self, button, hover, event):
        """Handle button hover effects"""
        if hover:
            button['frameColor'] = (0.3, 0.3, 0.3, 0.8)
        else:
            button['frameColor'] = (0.2, 0.2, 0.2, 0.8)
    
    def cleanup(self):
        """Clean up resources"""
        self.frame.destroy() 