from panda3d.core import Point3, Vec3
import math

class CameraController:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        
        # Camera properties
        self.distance = 10.0  # Distance from player
        self.height = 5.0    # Height above player
        self.rotation = 0.0  # Rotation around player (degrees)
        self.pitch = -30.0   # Camera pitch (degrees)
        
        # Mouse properties
        self.mouse_sensitivity = 0.2
        self.last_mouse = None
        
        # Set up mouse control
        self.setup_mouse()
        
        # Initial camera position
        self.update_camera()
    
    def setup_mouse(self):
        """Set up mouse control for camera"""
        # Center mouse on start
        props = self.base.win.getProperties()
        self.base.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
        
        # Enable mouse watching
        self.base.taskMgr.add(self.mouse_task, "camera_mouse_task")
    
    def mouse_task(self, task):
        """Handle mouse movement for camera control"""
        if not self.base.mouseWatcherNode.hasMouse():
            return task.cont
        
        # Get mouse position
        mouse = self.base.mouseWatcherNode.getMouse()
        
        if self.last_mouse is not None:
            # Calculate mouse movement
            dx = mouse.getX() - self.last_mouse.getX()
            dy = mouse.getY() - self.last_mouse.getY()
            
            # Update camera angles
            self.rotation -= dx * self.mouse_sensitivity * 100
            self.pitch = max(-80, min(30, self.pitch + dy * self.mouse_sensitivity * 100))
            
            # Update camera position
            self.update_camera()
            
            # Reset mouse to center
            props = self.base.win.getProperties()
            self.base.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
            return task.cont
        
        self.last_mouse = mouse
        return task.cont
    
    def update_camera(self):
        """Update camera position based on current settings"""
        if not hasattr(self.game_manager, 'player'):
            return
        
        # Get player position
        player_pos = self.game_manager.player.actor.getPos()
        
        # Calculate camera position
        angle_rad = math.radians(self.rotation)
        pitch_rad = math.radians(self.pitch)
        
        # Calculate horizontal distance and height
        horiz_dist = self.distance * math.cos(pitch_rad)
        height = self.distance * math.sin(pitch_rad) + self.height
        
        # Calculate camera position
        cam_x = player_pos.getX() - horiz_dist * math.sin(angle_rad)
        cam_y = player_pos.getY() - horiz_dist * math.cos(angle_rad)
        cam_z = player_pos.getZ() + height
        
        # Update camera
        self.base.camera.setPos(cam_x, cam_y, cam_z)
        self.base.camera.lookAt(
            player_pos.getX(),
            player_pos.getY(),
            player_pos.getZ() + self.height * 0.3  # Look slightly above player
        )
    
    def cleanup(self):
        """Clean up resources"""
        self.base.taskMgr.remove("camera_mouse_task")
        if hasattr(self, 'collision'):
            self.collision.removeNode() 