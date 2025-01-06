from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import BitMask32, Point3, Vec3
from panda3d.core import WindowProperties, TextNode, NodePath, PandaNode
from game.camera import ThirdPersonCamera
import math
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Wait, LerpPosInterval
from direct.gui.DirectWaitBar import DirectWaitBar

class Player(DirectObject):
    def __init__(self, base, collision_system, combat_system=None):
        super().__init__()
        self.base = base
        self.collision_system = collision_system
        self.combat_system = combat_system
        
        # Create physics character controller
        self.physics_node = self.collision_system.setup_player(self)
        
        # Set python tag for combat system
        self.physics_node.setPythonTag('owner', self)
        
        # Create visual representation (temporary cube)
        self.actor = self.base.loader.loadModel("models/box")
        self.actor.reparentTo(self.physics_node)
        self.actor.setScale(1, 1, 2)  # Make it a tall box for now
        self.actor.setPos(-0.5, -0.5, -1)  # Center it on the physics capsule
        self.actor.setColor(1, 0, 0, 1)  # Red color
        
        # Movement variables
        self.walk_speed = 15.0
        self.run_speed = 25.0  # Sprint speed
        self.move_speed = self.walk_speed
        self.jump_speed = 20.0  # Regular jump speed
        self.can_double_jump = True  # Whether we can perform a double jump
        self.has_double_jumped = False  # Whether we've used our double jump
        self.jump_pressed = False  # Track if jump key is currently pressed
        self.is_running = False
        
        # Combat variables
        self.health = 100
        self.max_health = 100
        self.is_attacking = False
        self.attack_cooldown = 0.5  # Time between attacks
        self.attack_timer = 0
        self.attack_damage = 20
        self.is_blocking = False
        self.block_damage_reduction = 0.5  # 50% damage reduction when blocking
        self.is_dodging = False
        self.dodge_cooldown = 1.0
        self.dodge_timer = 0
        self.dodge_speed_multiplier = 2.0
        self.dodge_duration = 0.3
        self.dodge_time_remaining = 0
        
        # Firing mode variables
        self.is_in_firing_mode = False
        self.crosshair = None
        self.original_cam_pos = None
        self.original_cam_parent = None
        
        # Lives system
        self.lives = 3
        self.max_lives = 5
        self.respawn_point = Point3(0, 0, 0)
        self.is_invulnerable = False
        self.invulnerability_duration = 2.0  # Seconds of invulnerability after respawn
        self.invulnerability_timer = 0
        
        # Create camera controller
        self.camera = ThirdPersonCamera(base, self.physics_node)
        self.heading = 0
        
        # Set up controls
        self.keys = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "jump": False,
            "run": False,
            "attack": False,
            "block": False,
            "dodge": False,
            "firing_mode": False
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
        self.accept("shift", self.updateKey, ["run", True])
        self.accept("shift-up", self.updateKey, ["run", False])
        self.accept("mouse1", self.updateKey, ["attack", True])
        self.accept("mouse1-up", self.updateKey, ["attack", False])
        self.accept("control", self.updateKey, ["dodge", True])
        self.accept("control-up", self.updateKey, ["dodge", False])
        self.accept("e", self.toggle_firing_mode)
        
        # Add update task
        self.base.taskMgr.add(self.update, "player_update")
        
        # Start with cursor visible and no mouse control
        self.mouse_enabled = False
        
        # Add first-person camera variables
        self.pitch = 0  # Track camera pitch separately
        self.mouse_sensitivity = 0.15  # Reduced sensitivity for smoother control
        self.camera_smoothing = 0.8  # Add smoothing factor
        self.target_heading = 0
        self.target_pitch = 0
        
        # Add gun model
        self.player_gun = None
        try:
            print("Creating simple gun model")
            # Create gun parts
            self.player_gun = self.base.render.attachNewNode("gun")
            
            # Create barrel (long cylinder)
            barrel = self.base.loader.loadModel("models/box")
            barrel.reparentTo(self.player_gun)
            barrel.setScale(0.1, 0.5, 0.1)  # Long and thin
            barrel.setPos(0, 0.5, 0)  # Extend forward
            barrel.setColor(0.2, 0.2, 0.2, 1)  # Dark gray
            
            # Create handle (box)
            handle = self.base.loader.loadModel("models/box")
            handle.reparentTo(self.player_gun)
            handle.setScale(0.1, 0.15, 0.3)  # Tall for grip
            handle.setPos(0, 0, -0.2)  # Below barrel
            handle.setColor(0.3, 0.3, 0.3, 1)  # Slightly lighter gray
            
            # Position gun relative to camera
            self.player_gun.reparentTo(self.base.camera)
            self.player_gun.setPos(0.3, 0.5, -0.3)  # Right, forward, and down from camera
            self.player_gun.setHpr(0, 0, 0)  # Level
            self.player_gun.hide()  # Hide until firing mode
            print("Gun model created successfully")
        except Exception as e:
            print("Error creating gun model:", str(e))
            print("Warning: Could not create gun model. Using raycast only.")
    
    def enable_mouse_control(self):
        """Enable mouse control and hide cursor"""
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.base.win.requestProperties(props)
        self.mouse_enabled = True
    
    def disable_mouse_control(self):
        """Disable mouse control and show cursor"""
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.base.win.requestProperties(props)
        self.mouse_enabled = False
    
    def updateKey(self, key, value):
        """Update the state of a key"""
        if key == "jump":
            print(f"Jump key {'pressed' if value else 'released'}")
        self.keys[key] = value
        
        # Handle running state
        if key == "run":
            self.move_speed = self.run_speed if value else self.walk_speed
    
    def take_damage(self, amount, knockback=None):
        """Handle player taking damage"""
        if self.is_invulnerable or self.health <= 0:  # Added check for health <= 0
            return False
            
        if self.is_blocking:
            amount *= (1 - self.block_damage_reduction)
        if not self.is_dodging:  # Invulnerable while dodging
            self.health = max(0, self.health - amount)
            
            # Notify HUD of health change
            if hasattr(self.base, 'hud'):
                self.base.hud.update_health(self.health, self.max_health)
            
            # Apply knockback if provided, but prevent falling through ground
            if knockback:
                current_pos = self.physics_node.getPos()
                new_pos = current_pos + knockback
                # Ensure minimum height
                new_pos.setZ(max(new_pos.getZ(), 0.5))  # Keep at least 0.5 units above ground
                self.physics_node.setPos(new_pos)
            
            if self.health <= 0:
                self.is_invulnerable = True  # Make invulnerable immediately when dying
                self.lose_life()
            return True
        return False
    
    def lose_life(self):
        """Handle losing a life"""
        self.lives -= 1
        
        # Update HUD with new lives count
        if hasattr(self.base, 'hud'):
            self.base.hud.update_lives(self.lives)
        
        if self.lives > 0:
            print(f"Lives remaining: {self.lives}")
            self.respawn()
            # Reset player position to level start
            if hasattr(self.base, 'current_level') and hasattr(self.base.current_level, 'spawn_point'):
                self.set_checkpoint(self.base.current_level.spawn_point)
                self.respawn()
        else:
            print("Game Over - No lives remaining")
            messenger.send('game_over')  # Signal game over to game manager
    
    def gain_life(self):
        """Add a life, up to max_lives"""
        if self.lives < self.max_lives:
            self.lives += 1
            return True
        return False
    
    def respawn(self):
        """Respawn the player at the last checkpoint"""
        self.health = self.max_health
        
        # Ensure spawn point is above ground
        spawn_pos = Point3(self.respawn_point)
        spawn_pos.setZ(max(spawn_pos.getZ(), 2.0))  # Ensure at least 2 units above ground
        self.physics_node.setPos(spawn_pos)
        
        # Set invulnerability
        self.is_invulnerable = True
        self.invulnerability_timer = self.invulnerability_duration
        
        # Notify HUD of health reset
        if hasattr(self.base, 'hud'):
            self.base.hud.update_health(self.health, self.max_health)
        
        # Reset movement states
        self.can_double_jump = True
        self.has_double_jumped = False
        self.jump_pressed = False
        self.is_dodging = False
        self.dodge_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        
        print(f"Player respawned at position: {spawn_pos}, invulnerable for {self.invulnerability_duration} seconds")
    
    def set_checkpoint(self, point):
        """Set a new respawn point"""
        self.respawn_point = Point3(point)
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        # Notify HUD of health change
        if hasattr(self.base, 'hud'):
            self.base.hud.update_health(self.health, self.max_health)
    
    def perform_attack(self):
        """Perform shooting attack"""
        # Only allow shooting in firing mode
        if not self.is_in_firing_mode:
            return False
            
        if not self.is_attacking and self.attack_timer <= 0 and self.combat_system:
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown
            
            # Simple gun animation - recoil
            if self.player_gun:
                # Save original position
                original_pos = self.player_gun.getPos()
                # Move back slightly
                self.player_gun.setPos(original_pos + Vec3(0, -0.1, 0))
                # Create sequence to return to original position
                Sequence(
                    Wait(0.05),  # Wait a bit
                    LerpPosInterval(self.player_gun, 0.1, original_pos)  # Smooth return
                ).start()
            
            # Use gun combat system to shoot
            self.combat_system.player_shoot(self)
            return True
        return False
    
    def perform_dodge(self):
        """Perform dodge roll"""
        if not self.is_dodging and self.dodge_timer <= 0:
            self.is_dodging = True
            self.dodge_timer = self.dodge_cooldown
            self.dodge_time_remaining = self.dodge_duration
            return True
        return False
    
    def toggle_firing_mode(self):
        """Toggle between normal and firing mode"""
        self.is_in_firing_mode = not self.is_in_firing_mode
        
        if self.is_in_firing_mode:
            # Store current camera settings
            self.original_cam_pos = self.base.camera.getPos()
            self.original_cam_parent = self.base.camera.getParent()
            
            # Get current camera heading and pitch
            current_h = self.base.camera.getH()
            current_p = self.base.camera.getP()
            
            # Switch to first person view
            self.base.camera.reparentTo(self.physics_node)
            self.base.camera.setPos(0, 0, 1.5)  # Up from player center
            self.base.camera.setHpr(current_h, current_p, 0)  # Maintain camera orientation
            self.heading = current_h
            self.pitch = current_p
            
            # Show gun model
            if self.player_gun:
                self.player_gun.show()
            
            # Create crosshair if it doesn't exist
            if not self.crosshair:
                self.crosshair = OnscreenImage(
                    image="assets/textures/crosshair.png",
                    pos=(0, 0, 0),
                    scale=0.05
                )
                self.crosshair.setTransparency(True)
            self.crosshair.show()
        else:
            # Hide crosshair and gun
            if self.crosshair:
                self.crosshair.hide()
            if self.player_gun:
                self.player_gun.hide()
            
            # Get current camera heading and pitch
            current_h = self.base.camera.getH()
            current_p = self.base.camera.getP()
            
            # Restore third person camera
            self.base.camera.reparentTo(self.original_cam_parent)
            self.camera.setup_camera()  # Reset camera position
            self.base.camera.setHpr(current_h, current_p, 0)  # Maintain orientation
            self.heading = current_h
    
    def get_camera_direction(self):
        """Get the direction the camera is facing"""
        if self.is_in_firing_mode:
            # In first person mode, use camera direction directly
            return self.base.camera.getQuat(self.base.render)
        else:
            # In third person mode, use player's facing direction
            quat = self.physics_node.getQuat(self.base.render)
            return quat
    
    def update(self, task):
        """Update player position and state"""
        dt = globalClock.getDt()
        
        # Update invulnerability
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                self.actor.setColor(1, 0, 0, 1)  # Reset to normal color
            else:
                # Flash the model while invulnerable
                alpha = 0.3 + 0.7 * ((int(self.invulnerability_timer * 10) % 2))
                self.actor.setColor(1, 0, 0, alpha)
        
        # Update timers
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
        
        if self.dodge_timer > 0:
            self.dodge_timer -= dt
        
        if self.is_dodging:
            self.dodge_time_remaining -= dt
            if self.dodge_time_remaining <= 0:
                self.is_dodging = False
        
        # Handle jumping
        on_ground = self.physics_node.node().isOnGround()
        
        # Reset jump states when landing
        if on_ground:
            self.can_double_jump = True
            self.has_double_jumped = False
            self.jump_pressed = False
        
        # Handle jump input
        if self.keys["jump"]:
            if not self.jump_pressed:  # Only jump if key wasn't pressed last frame
                if on_ground:
                    # Regular jump
                    print("Performing regular jump")
                    self.physics_node.node().setJumpSpeed(self.jump_speed)
                    self.physics_node.node().doJump()
                    self.jump_pressed = True
                elif self.can_double_jump and not self.has_double_jumped:
                    # Double jump
                    print("Performing double jump")
                    # Apply an upward impulse for double jump
                    self.physics_node.node().setLinearMovement(Vec3(0, 0, self.jump_speed), False)
                    self.has_double_jumped = True
                    self.can_double_jump = False
                    self.jump_pressed = True
        else:
            self.jump_pressed = False  # Reset when key is released
        
        # Only process mouse movement if enabled
        mouse_x = 0
        mouse_y = 0
        if self.mouse_enabled and self.base.mouseWatcherNode.hasMouse():
            mouse_x = self.base.mouseWatcherNode.getMouseX()
            mouse_y = self.base.mouseWatcherNode.getMouseY()
            
            # Center the mouse
            self.base.win.movePointer(0, 
                int(self.base.win.getXSize() / 2), 
                int(self.base.win.getYSize() / 2))
        
        # Handle camera movement
        if self.is_in_firing_mode:
            if self.mouse_enabled and self.base.mouseWatcherNode.hasMouse():
                # Get mouse movement
                mouse_x = self.base.mouseWatcherNode.getMouseX()
                mouse_y = self.base.mouseWatcherNode.getMouseY()
                
                # Update target heading and pitch
                self.target_heading -= mouse_x * self.mouse_sensitivity * 100
                self.target_pitch += mouse_y * self.mouse_sensitivity * 100
                self.target_pitch = max(-85, min(85, self.target_pitch))  # Clamp pitch
                
                # Smoothly interpolate current heading and pitch
                self.heading = (self.heading * self.camera_smoothing + 
                              self.target_heading * (1 - self.camera_smoothing))
                self.pitch = (self.pitch * self.camera_smoothing + 
                            self.target_pitch * (1 - self.camera_smoothing))
                
                # Apply camera rotation
                self.physics_node.setH(self.heading)
                self.base.camera.setP(self.pitch)
                
                # Center the mouse
                self.base.win.movePointer(0, 
                    int(self.base.win.getXSize() / 2), 
                    int(self.base.win.getYSize() / 2))
        else:
            # Third person camera update
            self.heading = self.camera.update(dt, mouse_x, mouse_y, self.mouse_enabled)
            self.physics_node.setH(self.heading)
            self.target_heading = self.heading  # Keep target in sync for mode switching
        
        # Handle shooting
        if self.keys["attack"]:
            self.perform_attack()
        
        # Get movement vectors from camera
        if self.is_in_firing_mode:
            # In first person, use camera's direction
            heading_rad = math.radians(self.heading)
            forward = Vec3(-math.sin(heading_rad), math.cos(heading_rad), 0)  # Fixed direction
            right = Vec3(math.cos(heading_rad), math.sin(heading_rad), 0)
        else:
            # In third person, use camera's vectors
            forward, right = self.camera.get_movement_basis()
        
        # Calculate movement direction
        movement = Vec3(0, 0, 0)
        
        # Add movement based on keys
        if self.keys["forward"]:
            movement += forward
        if self.keys["backward"]:
            movement -= forward
        if self.keys["right"]:
            movement += right
        if self.keys["left"]:
            movement -= right
        
        # Apply movement if any keys are pressed
        if movement.length() > 0:
            movement.normalize()
            # Reduce speed in firing mode
            if self.is_in_firing_mode:
                movement *= (self.move_speed * 0.7)  # 70% speed when in firing mode
            else:
                movement *= self.move_speed
            
            # Apply dodge speed multiplier if dodging
            if self.is_dodging:
                movement *= self.dodge_speed_multiplier
            
            # Ensure we're not moving too fast by clamping the movement vector
            max_speed = self.run_speed * 1.5  # Maximum allowed speed
            if movement.length() > max_speed:
                movement.normalize()
                movement *= max_speed
            
            # Apply movement with ground check
            if self.physics_node.node().isOnGround() or not self.is_in_firing_mode:
                self.physics_node.node().setLinearMovement(movement, True)
            else:
                # Reduce air control in firing mode
                movement *= 0.3
                self.physics_node.node().setLinearMovement(movement, True)
        else:
            self.physics_node.node().setLinearMovement(Vec3(0, 0, 0), True)
        
        return task.cont
    
    def cleanup(self):
        """Clean up player resources"""
        # Remove tasks
        self.base.taskMgr.remove("player_update")
        
        # Clean up camera
        if self.camera:
            self.camera.cleanup()
        
        # Clean up gun model
        if self.player_gun:
            self.player_gun.removeNode()
        
        # Clean up crosshair
        if self.crosshair:
            self.crosshair.destroy()
        
        # Clean up actor
        if self.actor:
            self.actor.removeNode()
        
        # Clean up physics node
        if self.physics_node:
            self.physics_node.removeNode()
        
        # Ignore all events
        self.ignoreAll() 