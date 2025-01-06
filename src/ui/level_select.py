from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectScrolledFrame,
    DirectLabel,
    DGG
)
from panda3d.core import TextNode

class LevelSelect:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create main background frame
        self.frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.15, 0.9),  # Dark blue-gray background
            frameSize=(-1, 1, -0.8, 0.8),  # Reduced frame size
            pos=(0, 0, 0)
        )
        
        # Welcome text with player name
        player_name = self.game_manager.player_name or "Player"
        self.welcome_text = DirectLabel(
            text=f"Welcome, {player_name}!",
            text_scale=0.07,  # Reduced text size
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.65),  # Adjusted position
            parent=self.frame
        )
        
        # Title
        self.title = DirectLabel(
            text="Select Your Challenge",
            text_scale=0.05,  # Reduced text size
            text_fg=(0.8, 0.8, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.55),  # Adjusted position
            parent=self.frame
        )
        
        # Level data
        self.levels = [
            {
                'number': 1,
                'name': "The Journey Begins",
                'description': "Master the art of jumping! A series of platforms await as you begin your adventure.",
                'difficulty': "Easy",
                'color': (0.2, 0.6, 0.2, 1)  # Green for easy
            },
            {
                'number': 2,
                'name': "Combat Training",
                'description': "Face your first enemies and learn to use cover effectively. Watch out for patrols!",
                'difficulty': "Medium",
                'color': (0.6, 0.6, 0.2, 1)  # Yellow for medium
            },
            {
                'number': 3,
                'name': "Boss Battle",
                'description': "The final challenge! Use everything you've learned to defeat the boss and complete your journey.",
                'difficulty': "Hard",
                'color': (0.6, 0.2, 0.2, 1)  # Red for hard
            }
        ]
        
        # Create level selection cards
        self.level_cards = []
        for i, level in enumerate(self.levels):
            # Card background
            card = DirectFrame(
                frameColor=(0.15, 0.15, 0.2, 0.8),
                frameSize=(-0.8, 0.8, -0.18, 0.18),  # Slightly taller than before
                pos=(0, 0, 0.25 - (i * 0.4)),  # Reduced spacing between cards
                parent=self.frame,
                relief=DGG.FLAT
            )
            
            # Level number and name
            DirectLabel(
                text=f"Level {level['number']} - {level['name']}",
                text_scale=0.05,
                text_fg=level['color'],
                text_align=TextNode.ALeft,
                frameColor=(0, 0, 0, 0),
                pos=(-0.75, 0, 0.1),  # Adjusted position
                parent=card
            )
            
            # Difficulty
            DirectLabel(
                text=f"Difficulty: {level['difficulty']}",
                text_scale=0.035,
                text_fg=level['color'],
                text_align=TextNode.ALeft,
                frameColor=(0, 0, 0, 0),
                pos=(-0.75, 0, 0.04),  # Adjusted position
                parent=card
            )
            
            # Description (with word wrap)
            DirectLabel(
                text=level['description'],
                text_scale=0.035,
                text_fg=(0.9, 0.9, 0.9, 1),
                text_align=TextNode.ALeft,
                text_wordwrap=50,
                frameColor=(0, 0, 0, 0),
                pos=(-0.75, 0, -0.02),  # Adjusted position
                parent=card
            )
            
            # Play button
            play_button = DirectButton(
                text="Play",
                text_scale=0.04,
                text_pos=(0, -0.01),
                text_fg=(1, 1, 1, 1),
                frameSize=(-0.12, 0.12, -0.04, 0.04),
                frameColor=level['color'],
                relief=DGG.FLAT,
                pos=(0.65, 0, -0.1),  # Adjusted position
                parent=card,
                command=self.on_level_select,
                extraArgs=[level]
            )
            
            # Hover effects
            card.bind(DGG.ENTER, self.on_card_hover, [card, True])
            card.bind(DGG.EXIT, self.on_card_hover, [card, False])
            play_button.bind(DGG.ENTER, self.on_button_hover, [play_button])
            play_button.bind(DGG.EXIT, self.on_button_exit, [play_button])
            
            self.level_cards.append(card)
        
        # Back button
        self.back_button = DirectButton(
            text="Back to Menu",
            text_scale=0.04,
            text_pos=(0, -0.01),
            frameSize=(-0.15, 0.15, -0.04, 0.04),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(-0.8, 0, 0.65),  # Moved to top-left corner
            parent=self.frame,
            command=self.on_back
        )
        self.back_button.bind(DGG.ENTER, self.on_button_hover, [self.back_button])
        self.back_button.bind(DGG.EXIT, self.on_button_exit, [self.back_button])
        
        # Show the menu
        self.show()
    
    def on_card_hover(self, card, hover, event):
        """Handle card hover effect"""
        if hover:
            card['frameColor'] = (0.2, 0.2, 0.25, 0.8)  # Lighter when hovered
        else:
            card['frameColor'] = (0.15, 0.15, 0.2, 0.8)  # Normal color
    
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
    
    def on_level_select(self, level_data):
        """Handle level selection"""
        self.hide()
        self.game_manager.start_level(level_data['number'])
    
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
    
    def cleanup(self):
        """Clean up resources"""
        self.frame.destroy() 