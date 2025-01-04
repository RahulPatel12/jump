from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DGG
)
from panda3d.core import TextNode

class LeaderboardMenu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            pos=(0, 0, 0)
        )
        
        # Create title
        self.title = DirectButton(
            text="Leaderboard",
            text_scale=0.12,
            text_pos=(0, -0.04),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.6),
            parent=self.frame
        )
        
        # Back button
        self.back_button = DirectButton(
            text="Back",
            command=self.on_back,
            pos=(0, 0, -0.6),
            parent=self.frame,
            frameSize=(-0.2, 0.2, -0.06, 0.06),
            text_scale=0.05,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=True
        )
        
        # Bind hover effects
        self.back_button.bind(DGG.ENTER, self.on_button_hover, [self.back_button])
        self.back_button.bind(DGG.EXIT, self.on_button_exit, [self.back_button])
    
    def on_button_hover(self, button, event):
        button['frameColor'] = (0.3, 0.3, 0.3, 0.8)
    
    def on_button_exit(self, button, event):
        button['frameColor'] = (0.2, 0.2, 0.2, 0.8)
    
    def on_back(self):
        self.game_manager.request('MainMenu')
    
    def cleanup(self):
        self.frame.destroy() 