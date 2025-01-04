from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectWaitBar,
    DGG
)
from panda3d.core import TextNode

class HUD:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create main frame for HUD elements
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 1, -1, 1),
            pos=(0, 0, 0)
        )
        
        # Score display
        self.score_label = DirectLabel(
            text="Score: 0",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.95, 0, 0.9),
            parent=self.frame
        )
        
        # Lives display
        self.lives_label = DirectLabel(
            text="Lives: 3",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.95, 0, 0.85),
            parent=self.frame
        )
        
        # Level name display
        self.level_label = DirectLabel(
            text="Level 1",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.9),
            parent=self.frame
        )
        
        # Health bar
        self.health_bar = DirectWaitBar(
            range=100,
            value=100,
            barColor=(0.2, 0.8, 0.2, 1),
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.3, 0.3, -0.015, 0.015),
            pos=(-0.65, 0, 0.85),
            parent=self.frame
        )
        
        # Objective display
        self.objective_label = DirectLabel(
            text="",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-0.5, 0.5, -0.05, 0.05),
            pos=(0, 0, -0.8),
            parent=self.frame
        )
        self.objective_label.hide()
    
    def update_score(self, score):
        """Update the score display"""
        self.score_label["text"] = f"Score: {score}"
    
    def update_lives(self, lives):
        """Update the lives display"""
        self.lives_label["text"] = f"Lives: {lives}"
    
    def update_health(self, health):
        """Update the health bar"""
        self.health_bar["value"] = health
    
    def set_level_name(self, name):
        """Set the level name display"""
        self.level_label["text"] = name
    
    def set_objective(self, text):
        """Set and show the current objective"""
        if text:
            self.objective_label["text"] = text
            self.objective_label.show()
        else:
            self.objective_label.hide()
    
    def cleanup(self):
        """Clean up resources"""
        self.frame.destroy() 