from panda3d.core import (
    Point3, Vec3, NodePath, GeomNode,
    Plane, CollisionPlane, CollisionNode,
    CardMaker, CollisionBox
)
from direct.showbase.DirectObject import DirectObject
import math

class Level(DirectObject):
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Initialize lists for platforms and obstacles
        self.platforms = []
        self.obstacles = []
        
        # Create ground plane
        self.create_ground_plane()
        
        # Set up initial platforms
        self.setup_initial_platforms()
    
    def create_ground_plane(self):
        """Create a visible ground plane with proper collision"""
        # Create visual ground plane
        from panda3d.core import CardMaker
        
        # Create a large but finite ground plane
        ground_size = 200  # Increased from 100 to 200 units
        maker = CardMaker('ground')
        maker.setFrame(-ground_size/2, ground_size/2, -ground_size/2, ground_size/2)
        
        # Create the ground node
        self.ground = self.base.render.attachNewNode(maker.generate())
        self.ground.setPos(0, 0, 0)
        self.ground.setP(-90)  # Rotate to be horizontal
        
        # Set ground color (darker green)
        self.ground.setColor(0.2, 0.5, 0.2, 1)
        
        # Add grid lines
        grid_spacing = 10  # Increased spacing for larger ground
        grid_color = (0.3, 0.6, 0.3, 1)  # Slightly lighter green
        
        for i in range(-int(ground_size/2), int(ground_size/2) + 1, grid_spacing):
            # Create vertical lines
            line = CardMaker(f'grid_line_v_{i}')
            line.setFrame(i, i + 0.1, -ground_size/2, ground_size/2)  # Vertical lines
            vline = self.base.render.attachNewNode(line.generate())
            vline.setP(-90)
            vline.setPos(0, 0, 0.01)  # Slightly above ground
            vline.setColor(*grid_color)
            self.platforms.append(vline)  # Store for cleanup
            
            # Create horizontal lines
            line = CardMaker(f'grid_line_h_{i}')
            line.setFrame(-ground_size/2, ground_size/2, i, i + 0.1)  # Horizontal lines
            hline = self.base.render.attachNewNode(line.generate())
            hline.setP(-90)
            hline.setPos(0, 0, 0.01)  # Slightly above ground
            hline.setColor(*grid_color)
            self.platforms.append(hline)  # Store for cleanup
        
        # Create collision plane
        collision_node = CollisionNode('ground_collision')
        # Create a collision plane facing upward at exactly ground level
        # Note: The plane's normal should point up (0, 0, 1) and we position it at y=0
        collision_plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        collision_node.addSolid(collision_plane)
        
        # Create a parent node for proper positioning
        collision_parent = self.base.render.attachNewNode("ground_collision_parent")
        collision_parent.setPos(0, 0, 0)  # Position at origin
        
        # Attach collision node to the parent
        collision_np = collision_parent.attachNewNode(collision_node)
        
        # Set collision masks
        collision_node.setFromCollideMask(0)
        collision_node.setIntoCollideMask(self.game_manager.collision_system.MASK_TERRAIN)
        
        # Store the collision node for cleanup
        self.ground_collision = collision_parent
    
    def setup_initial_platforms(self):
        """Set up the initial platforms for the level"""
        # Add platforms here when needed
        pass
    
    def cleanup(self):
        """Clean up level resources"""
        if hasattr(self, 'ground'):
            self.ground.removeNode()
        
        # Clean up platforms
        for platform in self.platforms:
            platform.removeNode()
        self.platforms.clear()
        
        # Clean up obstacles
        for obstacle in self.obstacles:
            obstacle.removeNode()
        self.obstacles.clear() 