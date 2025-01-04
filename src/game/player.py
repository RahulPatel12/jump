from direct.actor.Actor import Actor
from panda3d.core import Point3, Vec3, CardMaker, WindowProperties
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
import math

class Player(DirectObject):
    def __init__(self, base, collision_system):
        super().__init__()
        self.base = base
        self.collision_system = collision_system
        
        # Create a temporary card as the player model
        cm = CardMaker('player_card')
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)  # 1x1 card
        self.actor = self.base.render.attachNewNode(cm.generate())
        self.actor.setColor(1, 0, 0, 1)  # Red color
        self.actor.setPos(0, 0, 0.5)  # Slightly above ground
        
        # Movement variables
        self.velocity = Vec3(0, 0, 0)
        self.move_speed = 15.0  # Units per second
        self.acceleration = 40.0  # Units per second squared
        self.friction = 0.85  # Velocity multiplier per second
        self.jump_force = 15.0
        self.gravity = -30.0
        self.on_ground = False
        
        # Camera variables
        self.camera_height = 2.0
        self.camera_distance = 5.0
        self.camera_pitch = -15.0  # Degrees
        self.mouse_sensitivity = 20  # Increased from 0.2
        self.pitch_limits = (-80, 80)  # Limit vertical rotation
        self.heading = 0  # Player's heading in degrees
        
        # Center mouse and hide cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        
        # Add update tasks
        self.base.taskMgr.add(self.update, "player_update")
        self.base.taskMgr.add(self.update_camera, "camera_update")
        
        # Set up controls
        self.keys = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "jump": False
        }
        
        # Bind keys
        self.accept("w", self.updateKey, ["forward", True])
        self.accept("w-up", self.updateKey, ["forward", False])
        self.accept("s", self.updateKey, ["backward", True])
        self.accept("s-up", self.updateKey, ["backward", False])
        self.accept("a", self.updateKey, ["left", True])
        self.accept("a-up", self.updateKey, ["left", False])
        self.accept("d", self.updateKey, ["right", True])
        self.accept("d-up", self.updateKey, ["right", False])
        self.accept("space", self.updateKey, ["jump", True])
        self.accept("space-up", self.updateKey, ["jump", False])
    
    def updateKey(self, key, value):
        """Update the state of a key"""
        self.keys[key] = value
    
    def update(self, task):
        """Update player position and state"""
        dt = globalClock.getDt()
        
        # Get mouse movement for turning
        if self.base.mouseWatcherNode.hasMouse():
            mouse_x = self.base.mouseWatcherNode.getMouseX()
            mouse_y = self.base.mouseWatcherNode.getMouseY()
            
            # Center the mouse
            self.base.win.movePointer(0, 
                int(self.base.win.getXSize() / 2), 
                int(self.base.win.getYSize() / 2))
            
            # Update player heading and camera pitch
            self.heading -= mouse_x * self.mouse_sensitivity * 100 * dt
            self.camera_pitch += mouse_y * self.mouse_sensitivity * 100 * dt
            
            # Clamp the pitch to prevent over-rotation
            self.camera_pitch = max(self.pitch_limits[0], min(self.pitch_limits[1], self.camera_pitch))
            
            # Update player model rotation (only horizontal)
            self.actor.setH(self.heading)
        
        # Get movement direction in player's local space
        move_dir = Vec3(0, 0, 0)
        if self.keys["forward"]:
            move_dir.setY(1)
        if self.keys["backward"]:
            move_dir.setY(-1)
        if self.keys["left"]:
            move_dir.setX(-1)
        if self.keys["right"]:
            move_dir.setX(1)
        
        # Convert to world space based on player's heading
        if move_dir.length() > 0:
            move_dir.normalize()
            heading_rad = math.radians(self.heading)
            cos_h = math.cos(heading_rad)
            sin_h = math.sin(heading_rad)
            
            # Rotate movement vector by heading
            world_move = Vec3(
                move_dir.getX() * cos_h + move_dir.getY() * sin_h,
                -move_dir.getX() * sin_h + move_dir.getY() * cos_h,
                0
            )
            
            # Apply acceleration
            self.velocity.setX(self.velocity.getX() + world_move.getX() * self.acceleration * dt)
            self.velocity.setY(self.velocity.getY() + world_move.getY() * self.acceleration * dt)
        
        # Apply friction to horizontal movement
        friction = math.pow(self.friction, dt * 60)  # Adjust friction based on frame rate
        self.velocity.setX(self.velocity.getX() * friction)
        self.velocity.setY(self.velocity.getY() * friction)
        
        # Limit horizontal speed
        speed = Vec3(self.velocity.getX(), self.velocity.getY(), 0).length()
        if speed > self.move_speed:
            scale = self.move_speed / speed
            self.velocity.setX(self.velocity.getX() * scale)
            self.velocity.setY(self.velocity.getY() * scale)
        
        # Apply gravity
        self.velocity.setZ(self.velocity.getZ() + self.gravity * dt)
        
        # Handle jumping
        if self.keys["jump"] and self.on_ground:
            self.velocity.setZ(self.jump_force)
            self.on_ground = False
        
        # Move player
        new_pos = self.actor.getPos() + self.velocity * dt
        
        # Ground collision check
        if new_pos.getZ() < 0.5:  # 0.5 is half height of player
            new_pos.setZ(0.5)
            self.velocity.setZ(0)
            self.on_ground = True
        else:
            self.on_ground = False
        
        self.actor.setPos(new_pos)
        
        return Task.cont
    
    def update_camera(self, task):
        """Update camera position and orientation"""
        # Calculate camera position
        cam_height = self.camera_height
        cam_distance = self.camera_distance
        
        # Calculate camera offset based on heading and pitch
        heading_rad = math.radians(self.heading)
        pitch_rad = math.radians(self.camera_pitch)
        
        # Calculate horizontal distance based on pitch
        horiz_dist = cam_distance * math.cos(pitch_rad)
        
        # Calculate camera position relative to player
        cam_x = self.actor.getX() - math.sin(heading_rad) * horiz_dist
        cam_y = self.actor.getY() - math.cos(heading_rad) * horiz_dist
        cam_z = self.actor.getZ() + cam_height + cam_distance * math.sin(pitch_rad)
        
        # Set camera position and make it look at player
        self.base.camera.setPos(cam_x, cam_y, cam_z)
        
        # Make camera look at a point slightly above the player
        look_at_height = self.actor.getZ() + 1.0  # Look at point 1 unit above player
        self.base.camera.lookAt(
            self.actor.getX(),
            self.actor.getY(),
            look_at_height
        )
        
        return Task.cont
    
    def cleanup(self):
        """Clean up resources"""
        self.base.taskMgr.remove("player_update")
        self.base.taskMgr.remove("camera_update")
        self.actor.removeNode()
        
        # Show cursor
        props = WindowProperties()
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)
        
        # Unbind keys
        self.ignore("w")
        self.ignore("w-up")
        self.ignore("s")
        self.ignore("s-up")
        self.ignore("a")
        self.ignore("a-up")
        self.ignore("d")
        self.ignore("d-up")
        self.ignore("space")
        self.ignore("space-up") 