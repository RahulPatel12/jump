from panda3d.core import CardMaker

class Level:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Create ground plane
        cm = CardMaker('ground')
        cm.setFrame(-20, 20, -20, 20)  # 40x40 unit ground
        self.ground = self.base.render.attachNewNode(cm.generate())
        self.ground.setP(-90)  # Rotate to be horizontal
        self.ground.setPos(0, 0, 0)  # At origin
        self.ground.setColor(0.2, 0.5, 0.2, 1)  # Darker green
        
        # Add a grid pattern to the ground
        for i in range(-20, 21, 2):
            # Create grid lines
            line = CardMaker(f'grid_line_{i}')
            line.setFrame(i, i + 0.05, -20, 20)  # Vertical lines
            vline = self.base.render.attachNewNode(line.generate())
            vline.setP(-90)
            vline.setPos(0, 0, 0.01)  # Slightly above ground
            vline.setColor(0.3, 0.6, 0.3, 1)  # Slightly lighter green
            
            line = CardMaker(f'grid_line_h_{i}')
            line.setFrame(-20, 20, i, i + 0.05)  # Horizontal lines
            hline = self.base.render.attachNewNode(line.generate())
            hline.setP(-90)
            hline.setPos(0, 0, 0.01)  # Slightly above ground
            hline.setColor(0.3, 0.6, 0.3, 1)  # Slightly lighter green
        
        # Level properties
        self.objective = "Collect all coins and reach the goal!"
    
    def pause_physics(self):
        """Pause level physics"""
        pass  # No physics yet
    
    def resume_physics(self):
        """Resume level physics"""
        pass  # No physics yet
    
    def cleanup(self):
        """Clean up level resources"""
        if hasattr(self, 'ground'):
            self.ground.removeNode() 