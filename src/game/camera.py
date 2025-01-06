from panda3d.core import Point3, PandaNode

class ThirdPersonCamera:
    def __init__(self, base, target_node):
        self.base = base
        self.target_node = target_node
        
        # Camera variables
        self.height = 1.5
        self.distance = 12.0
        self.min_distance = 5.0  # Minimum zoom distance
        self.max_distance = 20.0  # Maximum zoom distance
        self.zoom_speed = 1.0    # How fast to zoom per wheel tick
        self.pitch = -10.0
        self.heading = 0.0
        self.mouse_sensitivity = 15.0
        self.pitch_limits = (-85, 85)
        
        # Create camera rig
        self.camera_base = target_node.attachNewNode(PandaNode("camera-base"))
        self.camera_holder = self.camera_base.attachNewNode(PandaNode("camera-holder"))
        self.base.camera.reparentTo(self.camera_holder)
        
        # Set initial camera position
        self.setup_camera()
        
        # Bind zoom controls
        self.base.accept("wheel_up", self.zoom_in)
        self.base.accept("wheel_down", self.zoom_out)
    
    def setup_camera(self):
        """Set up initial camera position and orientation"""
        self.camera_base.setPos(0, 0, self.height)  # Center the pivot point
        self.camera_base.setP(self.pitch)
        self.camera_holder.setY(-self.distance)
        self.camera_holder.setX(0)  # Ensure horizontal centering
        
        # Make camera look at target's center point
        target_point = Point3(0, 0, 0.5)  # Slightly above target's base
        self.base.camera.lookAt(target_point)
    
    def update(self, dt, mouse_x=0, mouse_y=0, mouse_enabled=False):
        """Update camera position and rotation"""
        if mouse_enabled:
            # Update heading and pitch based on mouse movement
            self.heading += mouse_x * self.mouse_sensitivity * 100 * dt
            self.pitch += mouse_y * self.mouse_sensitivity * 100 * dt
            
            # Clamp the pitch to prevent over-rotation
            self.pitch = max(self.pitch_limits[0], min(self.pitch_limits[1], self.pitch))
            
            # Update camera rig rotation
            self.camera_base.setH(self.heading)
            self.camera_base.setP(self.pitch)
            
            # Make camera look at target's center
            self.base.camera.lookAt(self.target_node)
        
        return self.heading  # Return heading for player rotation
    
    def get_movement_basis(self):
        """Get forward and right vectors for movement relative to camera view"""
        # Get the camera's forward vector
        forward = self.camera_base.getMat().getRow3(1)
        forward.setZ(0)  # Keep movement horizontal
        forward.normalize()
        
        # Get the camera's right vector
        right = self.camera_base.getMat().getRow3(0)
        right.setZ(0)  # Keep movement horizontal
        right.normalize()
        
        return forward, right
    
    def zoom_in(self):
        """Zoom camera in"""
        self.distance = max(self.min_distance, self.distance - self.zoom_speed)
        self.camera_holder.setY(-self.distance)
    
    def zoom_out(self):
        """Zoom camera out"""
        self.distance = min(self.max_distance, self.distance + self.zoom_speed)
        self.camera_holder.setY(-self.distance)
    
    def cleanup(self):
        """Clean up camera resources"""
        # Unbind zoom controls
        self.base.ignore("wheel_up")
        self.base.ignore("wheel_down")
        self.camera_holder.removeNode()
        self.camera_base.removeNode() 