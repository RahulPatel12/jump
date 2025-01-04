from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectLabel,
    DirectScrolledFrame,
    DGG
)
from panda3d.core import TextNode

class Leaderboard:
    def __init__(self, base):
        self.base = base
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = DirectLabel(
            text="Leaderboard",
            text_scale=0.1,
            text_pos=(0, -0.03),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.6),
            parent=self.frame
        )
        
        # Create scrolled frame for scores
        self.scores_frame = DirectScrolledFrame(
            frameSize=(-0.7, 0.7, -0.5, 0.5),
            canvasSize=(-0.65, 0.65, -1, 1),
            frameColor=(0.1, 0.1, 0.1, 0.8),
            scrollBarWidth=0.04,
            parent=self.frame,
            pos=(0, 0, 0)
        )
        
        # Create column headers
        self.create_headers()
        
        # Create refresh button
        self.refresh_button = DirectButton(
            text="Refresh",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.1, 0.1, -0.05, 0.05),
            frameColor=(0.2, 0.5, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0.6, 0, -0.7),
            parent=self.frame,
            command=self.on_refresh
        )
        
        # Create back button
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
        
        # Set up button hover effects
        for button in [self.refresh_button, self.back_button]:
            button.bind(DGG.ENTER, self.on_button_hover, [button, True])
            button.bind(DGG.EXIT, self.on_button_hover, [button, False])
        
        # Initially hide the menu
        self.hide()
        
        # Load scores
        self.load_scores()
    
    def create_headers(self):
        """Create column headers for the leaderboard"""
        headers = [
            ("Rank", -0.55),
            ("Player", -0.35),
            ("Score", -0.05),
            ("Level", 0.25),
            ("Date", 0.45)
        ]
        
        for text, x_pos in headers:
            DirectLabel(
                text=text,
                text_scale=0.05,
                text_pos=(0, -0.015),
                text_fg=(0.8, 0.8, 0.8, 1),
                text_align=TextNode.ACenter,
                frameColor=(0, 0, 0, 0),
                pos=(x_pos, 0, 0.9),
                parent=self.scores_frame.getCanvas()
            )
    
    def load_scores(self):
        """Load and display scores"""
        # Example scores - in real implementation, these would be loaded from a database or file
        scores = [
            (1, "Player1", 10000, "Level 5", "2024-01-02"),
            (2, "Player2", 9500, "Level 4", "2024-01-02"),
            (3, "Player3", 9000, "Level 5", "2024-01-01"),
            (4, "Player4", 8500, "Level 3", "2024-01-01"),
            (5, "Player5", 8000, "Level 4", "2024-01-01"),
            (6, "Player6", 7500, "Level 3", "2023-12-31"),
            (7, "Player7", 7000, "Level 4", "2023-12-31"),
            (8, "Player8", 6500, "Level 2", "2023-12-31"),
            (9, "Player9", 6000, "Level 3", "2023-12-30"),
            (10, "Player10", 5500, "Level 2", "2023-12-30")
        ]
        
        # Clear existing score entries
        for child in self.scores_frame.getCanvas().getChildren():
            if child.getName() == "score_entry":
                child.removeNode()
        
        # Create score entries
        for i, (rank, player, score, level, date) in enumerate(scores):
            y_pos = 0.8 - (i + 1) * 0.1
            
            # Background frame for the row (alternating colors)
            DirectFrame(
                frameColor=(0.15, 0.15, 0.15, 0.8) if i % 2 == 0 else (0.2, 0.2, 0.2, 0.8),
                frameSize=(-0.6, 0.6, -0.04, 0.04),
                pos=(0, 0, y_pos),
                parent=self.scores_frame.getCanvas(),
                name="score_entry"
            )
            
            # Score data
            positions = [
                (str(rank), -0.55),
                (player, -0.35),
                (str(score), -0.05),
                (level, 0.25),
                (date, 0.45)
            ]
            
            for text, x_pos in positions:
                DirectLabel(
                    text=text,
                    text_scale=0.04,
                    text_pos=(0, -0.01),
                    text_fg=(1, 1, 1, 1),
                    text_align=TextNode.ACenter,
                    frameColor=(0, 0, 0, 0),
                    pos=(x_pos, 0, y_pos),
                    parent=self.scores_frame.getCanvas(),
                    name="score_entry"
                )
    
    def on_refresh(self):
        """Handle refresh button click"""
        self.load_scores()
        print("Refreshing scores")
    
    def on_back(self):
        """Handle back button click"""
        self.hide()
        # TODO: Show main menu
        print("Back to main menu")
    
    def show(self):
        """Show the leaderboard"""
        self.frame.show()
    
    def hide(self):
        """Hide the leaderboard"""
        self.frame.hide()
    
    def on_button_hover(self, button, hover, event):
        """Handle button hover effects"""
        if hover:
            orig_color = button['frameColor']
            button['frameColor'] = (
                min(orig_color[0] + 0.1, 1.0),
                min(orig_color[1] + 0.1, 1.0),
                min(orig_color[2] + 0.1, 1.0),
                orig_color[3]
            )
        else:
            orig_color = button['frameColor']
            button['frameColor'] = (
                max(orig_color[0] - 0.1, 0.0),
                max(orig_color[1] - 0.1, 0.0),
                max(orig_color[2] - 0.1, 0.0),
                orig_color[3]
            ) 