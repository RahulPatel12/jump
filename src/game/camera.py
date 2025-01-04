from direct.task import Task
from panda3d.core import Point3, Vec3, LVector3f
from math import sin, cos, pi

class CameraController:
    # Constants
    CAMERA_DISTANCE = 10.0  # Distance from player
    CAMERA_HEIGHT = 5.0    # Height above player
    CAMERA_LAG = 0.1      # Camera smoothing factor
    MIN_ZOOM = 5.0        # Minimum zoom distance
    MAX_ZOOM = 20.0       # Maximum zoom distance
    MIN_PITCH = -50.0     # Minimum pitch angle (degrees)
    MAX_PITCH = 80.0      # Maximum pitch angle (degrees)
    
    def __init__(self, base, target):
        self.base = base
        self.target = target  # The player or object to follow
        
        # Camera state
        self.distance = self.CAMERA_DISTANCE
        self.heading = 0  # Rotation around Z axis (yaw)
        self.pitch = 30   # Rotation up/down (degrees)
        
        # Mouse control state
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_control_active = False
        
        # Current camera position for smooth movement
        self.current_pos = LVector3f(0, -self.distance, self.CAMERA_HEIGHT)
        
        # Disable default mouse control
        self.base.disableMouse()
        
        # Set up input handlers
        self.setup_input()
        
        # Start update task
        self.base.taskMgr.add(self.update, "camera_update")
    
    def setup_input(self):
        """Set up input handlers for camera control"""
        # Mouse control
        self.base.accept("mouse3", self.start_mouse_control)
        self.base.accept("mouse3-up", self.stop_mouse_control)
        
        # Zoom control
        self.base.accept("wheel_up", self.zoom_in)
        self.base.accept("wheel_down", self.zoom_out)
    
    def start_mouse_control(self):
        """Start camera rotation with mouse"""
        if self.base.mouseWatcherNode.hasMouse():
            self.mouse_control_active = True
            self.last_mouse_x = self.base.mouseWatcherNode.getMouseX()
            self.last_mouse_y = self.base.mouseWatcherNode.getMouseY()
    
    def stop_mouse_control(self):
        """Stop camera rotation"""
        self.mouse_control_active = False
    
    def zoom_in(self):
        """Handle mouse wheel zoom in"""
        self.distance = max(self.MIN_ZOOM, self.distance - 1.0)
    
    def zoom_out(self):
        """Handle mouse wheel zoom out"""
        self.distance = min(self.MAX_ZOOM, self.distance + 1.0)
    
    def update(self, task):
        """Update camera position and rotation"""
        # Update camera rotation from mouse input
        if self.mouse_control_active and self.base.mouseWatcherNode.hasMouse():
            mouse_x = self.base.mouseWatcherNode.getMouseX()
            mouse_y = self.base.mouseWatcherNode.getMouseY()
            
            # Calculate mouse movement
            dx = (mouse_x - self.last_mouse_x) * 100
            dy = (mouse_y - self.last_mouse_y) * 100
            
            # Update camera angles
            self.heading -= dx
            self.pitch += dy
            
            # Clamp pitch angle
            self.pitch = min(max(self.pitch, self.MIN_PITCH), self.MAX_PITCH)
            
            # Store current mouse position
            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y
        
        # Calculate ideal camera position
        pitch_rad = self.pitch * (pi / 180.0)
        heading_rad = self.heading * (pi / 180.0)
        
        # Calculate camera offset from target
        cam_x = self.distance * sin(heading_rad) * cos(pitch_rad)
        cam_y = self.distance * cos(heading_rad) * cos(pitch_rad)
        cam_z = self.distance * sin(pitch_rad) + self.CAMERA_HEIGHT
        
        target_pos = self.target.getPos()
        ideal_pos = Point3(
            target_pos.getX() + cam_x,
            target_pos.getY() + cam_y,
            target_pos.getZ() + cam_z
        )
        
        # Smoothly move camera to ideal position
        self.current_pos = (
            self.current_pos * (1 - self.CAMERA_LAG) +
            ideal_pos * self.CAMERA_LAG
        )
        
        # Update camera position and look at target
        self.base.camera.setPos(self.current_pos)
        self.base.camera.lookAt(target_pos)
        
        return Task.cont
    
    def cleanup(self):
        """Clean up camera controller"""
        self.base.taskMgr.remove("camera_update")
        self.base.enableMouse()  # Re-enable default mouse control 