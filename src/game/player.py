from direct.actor.Actor import Actor
from panda3d.core import Point3, Vec3, WindowProperties, NodePath, Loader
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
import math

class Player(DirectObject):
    def __init__(self, base, collision_system):
        super().__init__()
        self.base = base
        self.collision_system = collision_system
        
        # Create a basic 3D model for the player (temporary cube)
        # Later this can be replaced with a proper character model
        self.actor = self.create_player_model()
        self.actor.setPos(0, 0, 1)  # Start slightly above ground
        self.actor.reparentTo(self.base.render)
        
        # Movement variables
        self.velocity = Vec3(0, 0, 0)
        self.move_speed = 15.0
        self.acceleration = 40.0
        self.friction = 0.85
        self.jump_force = 15.0
        self.gravity = -30.0
        self.on_ground = False
        self.fall_threshold = -50  # Point at which player dies from falling
        
        # Camera variables
        self.camera_height = 1.5  # Adjusted down from 2.0
        self.camera_distance = 8.0  # Increased from 5.0 for better view
        self.camera_pitch = -15.0
        self.mouse_sensitivity = 20
        self.pitch_limits = (-80, 80)
        self.heading = 0
        
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
            "jump": False,
            "sprint": False
        }
        
        # Bind keys
        self.bind_keys()
        
        # Set up collision detection
        if self.collision_system:
            self.collision_system.setup_player_collisions(self)

    def create_player_model(self):
        """Create a basic 3D model for the player"""
        # Create a temporary cube model
        # This will be replaced with a proper character model later
        model = self.base.loader.loadModel("models/box")
        if not model:
            # If the box model isn't available, create a procedural cube
            from panda3d.core import GeomVertexFormat, GeomVertexData
            from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
            from panda3d.core import GeomNode
            
            # Create the vertex format
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('cube', format, Geom.UHStatic)
            
            # Create writers for vertex data
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            # Define the vertices
            vertices = [
                (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)
            ]
            
            # Add the vertices to the vertex data
            for v in vertices:
                vertex.addData3(*v)
                normal.addData3(0, 0, 1)  # Simple normal
                color.addData4(0.5, 0.5, 1.0, 1.0)  # Blue-ish color
            
            # Create the triangles
            prim = GeomTriangles(Geom.UHStatic)
            indices = [
                0, 1, 2, 0, 2, 3,  # Bottom
                4, 5, 6, 4, 6, 7,  # Top
                0, 4, 7, 0, 7, 3,  # Left
                1, 5, 6, 1, 6, 2,  # Right
                0, 1, 5, 0, 5, 4,  # Back
                3, 2, 6, 3, 6, 7   # Front
            ]
            
            # Add the indices to create the triangles
            for i in range(0, len(indices), 3):
                prim.addVertices(indices[i], indices[i + 1], indices[i + 2])
            
            # Create the geometry and node
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            node = GeomNode('player_cube')
            node.addGeom(geom)
            
            model = NodePath(node)
        
        # Scale the model to a reasonable size
        model.setScale(1, 1, 2)  # Make it twice as tall as wide
        return model

    def bind_keys(self):
        """Bind all player control keys"""
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
        self.accept("shift", self.updateKey, ["sprint", True])
        self.accept("shift-up", self.updateKey, ["sprint", False])
    
    def updateKey(self, key, value):
        """Update the state of a key"""
        self.keys[key] = value
        
        # Adjust movement speed when sprinting
        if key == "sprint":
            self.move_speed = 25.0 if value else 15.0
    
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
            self.heading += mouse_x * self.mouse_sensitivity * 100 * dt
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
                move_dir.getX() * cos_h - move_dir.getY() * sin_h,
                move_dir.getX() * sin_h + move_dir.getY() * cos_h,
                0
            )
            
            # Apply acceleration
            self.velocity.setX(self.velocity.getX() + world_move.getX() * self.acceleration * dt)
            self.velocity.setY(self.velocity.getY() + world_move.getY() * self.acceleration * dt)
        
        # Apply friction to horizontal movement
        friction = math.pow(self.friction, dt * 60)
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
        
        # Check if player has fallen too far
        if new_pos.getZ() < self.fall_threshold:
            # Reset player position (or implement death/respawn)
            new_pos = Point3(0, 0, 1)
            self.velocity = Vec3(0, 0, 0)
        
        # Update position
        self.actor.setPos(new_pos)
        
        # Update ground state using collision system
        if self.collision_system:
            self.on_ground = self.collision_system.check_ground_collision(self)
        
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
        
        # Set camera position
        self.base.camera.setPos(cam_x, cam_y, cam_z)
        
        # Make camera look at a point slightly above the player's center
        look_at_height = self.actor.getZ() + self.camera_height * 0.3  # Lowered from 0.5 to 0.3
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
        if self.actor:
            self.actor.removeNode()
        
        # Show cursor
        props = WindowProperties()
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)
        
        # Unbind keys
        self.ignoreAll() 