from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import (
    Point3, Vec3, NodePath, CollisionNode, CollisionRay, BitMask32,
    CollisionHandlerQueue
)
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import DirectWaitBar
import math
import random

class Enemy(FSM, DirectObject):
    def __init__(self, base, collision_system, combat_system, position):
        FSM.__init__(self, 'EnemyFSM')
        DirectObject.__init__(self)
        
        self.base = base
        self.collision_system = collision_system
        self.combat_system = combat_system
        
        # Create physics character controller
        self.physics_node = self.collision_system.setup_enemy(self)
        self.physics_node.setPos(position)
        
        # Set python tag for combat system
        self.physics_node.setPythonTag('owner', self)
        
        # Create visual representation (temporary cube)
        self.actor = self.base.loader.loadModel("models/box")
        self.actor.reparentTo(self.physics_node)
        self.actor.setScale(1, 1, 2)  # Make it a tall box for now
        self.actor.setPos(-0.5, -0.5, -1)  # Center it on the physics capsule
        self.actor.setColor(0.8, 0.2, 0.2, 1)  # Red color
        
        # Combat variables
        self.health = 100
        self.max_health = 100
        self.is_attacking = False
        self.attack_cooldown = 2.0  # Increased cooldown between shots (was 1.0)
        self.attack_timer = 0
        self.attack_damage = 15
        self.attack_range = 15.0  # Decreased range for shooting (was 20.0)
        self.detection_range = 20.0  # Decreased detection range (was 30.0)
        
        # Movement variables
        self.move_speed = 5.0
        self.target = None  # Current movement target
        self.path = []  # Path to target
        self.path_update_timer = 0
        self.path_update_interval = 0.5  # How often to update path
        self.min_distance = 5.0  # Reduced from 10.0 to allow closer approach
        self.strafe_time = 0  # Timer for strafing movement
        self.strafe_direction = Vec3(0, 0, 0)  # Current strafe direction
        
        # Create health bar
        self.health_bar = DirectWaitBar(
            range=100,
            value=100,
            barColor=(0.2, 0.8, 0.2, 1),  # Green color
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.5, 0.5, -0.05, 0.05),
            pos=(0, 0, 2),  # Position above enemy
            scale=0.5,
            parent=self.physics_node
        )
        self.health_bar.setBillboardPointEye()  # Make health bar always face camera
        
        # Add update task
        self.base.taskMgr.add(self.update, "enemy_update")
        
        # Start with idle state
        self.request('Idle')
    
    def take_damage(self, amount, knockback=None):
        """Handle enemy taking damage"""
        self.health = max(0, self.health - amount)
        
        # Update health bar
        self.health_bar['value'] = self.health
        
        # Update health bar color based on health percentage
        health_percent = self.health / self.max_health
        if health_percent > 0.6:
            self.health_bar['barColor'] = (0.2, 0.8, 0.2, 1)  # Green
        elif health_percent > 0.3:
            self.health_bar['barColor'] = (0.8, 0.8, 0.2, 1)  # Yellow
        else:
            self.health_bar['barColor'] = (0.8, 0.2, 0.2, 1)  # Red
        
        # Apply knockback if provided
        if knockback:
            current_pos = self.physics_node.getPos()
            new_pos = current_pos + knockback
            self.physics_node.setPos(new_pos)
        
        if self.health <= 0:
            self.die()
        else:
            # Enter combat mode when damaged
            self.request('Chase')
        return True
    
    def die(self):
        """Handle enemy death"""
        self.cleanup()
        messenger.send('enemy_defeated', [self])  # Signal defeat to game manager
    
    def perform_attack(self):
        """Perform shooting attack"""
        if not self.is_attacking and self.attack_timer <= 0:
            print("Enemy attempting to shoot")
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown
            # Use gun combat system to shoot
            success = self.combat_system.enemy_shoot(self)
            print(f"Enemy shoot result: {success}")
            return success
        else:
            print(f"Can't shoot - is_attacking: {self.is_attacking}, timer: {self.attack_timer:.1f}")
        return False
    
    def get_distance_to_player(self):
        """Get distance to player"""
        if not hasattr(self.base, 'player'):
            return float('inf')
        
        player_pos = self.base.player.physics_node.getPos()
        enemy_pos = self.physics_node.getPos()
        return (player_pos - enemy_pos).length()
    
    def get_direction_to_player(self):
        """Get normalized direction vector to player"""
        if not hasattr(self.base, 'player'):
            return Vec3(0, 0, 0)
        
        player_pos = self.base.player.physics_node.getPos()
        enemy_pos = self.physics_node.getPos()
        direction = player_pos - enemy_pos
        direction.normalize()
        return direction
    
    def update(self, task):
        """Update enemy state"""
        dt = globalClock.getDt()
        
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
        
        # Update path timer
        self.path_update_timer -= dt
        if self.path_update_timer <= 0:
            self.path_update_timer = self.path_update_interval
            self.update_path()
        
        # Update strafe timer
        self.strafe_time -= dt
        if self.strafe_time <= 0:
            # Change strafe direction randomly
            self.strafe_time = random.uniform(1.0, 2.0)
            angle = random.uniform(0, 2 * math.pi)
            self.strafe_direction = Vec3(math.cos(angle), math.sin(angle), 0)
        
        # Check distance to player and move accordingly
        distance = self.get_distance_to_player()
        if distance < self.detection_range:
            direction = self.get_direction_to_player()
            
            # Calculate movement
            movement = Vec3(0, 0, 0)
            
            # Move away if too close
            if distance < self.min_distance:
                movement -= direction * self.move_speed
            # Move closer if too far
            elif distance > self.attack_range:
                movement += direction * self.move_speed
            
            # Add strafing movement
            if self.strafe_direction.length() > 0:
                # Project strafe direction onto plane perpendicular to direction to player
                strafe = self.strafe_direction - direction * direction.dot(self.strafe_direction)
                strafe.normalize()
                movement += strafe * self.move_speed * 0.8  # Slightly slower strafe
            
            # Apply movement
            if movement.length() > 0:
                movement.normalize()
                self.physics_node.setPos(self.physics_node.getPos() + movement * dt)
                
                # Update rotation to face player
                heading = math.degrees(math.atan2(-direction.getX(), direction.getY()))
                self.physics_node.setH(heading)
            
            # Attack if in range and facing player
            if distance < self.attack_range:
                print(f"Enemy in attack range (distance: {distance:.1f})")
                # Check if we have line of sight
                has_los = self.has_line_of_sight()
                print(f"Has line of sight: {has_los}")
                if has_los:
                    attack_success = self.perform_attack()
                    print(f"Attack performed: {attack_success}, Timer: {self.attack_timer:.1f}")
        
        return task.cont
    
    def update_path(self):
        """Update path to target"""
        # Simple direct path for now
        # In a more complex implementation, this would use pathfinding
        if hasattr(self.base, 'player'):
            self.target = self.base.player.physics_node.getPos()
    
    def move_along_path(self, dt):
        """Move towards current target"""
        if self.target:
            direction = self.target - self.physics_node.getPos()
            distance = direction.length()
            
            if distance > 0.1:  # Only move if not at target
                direction.normalize()
                movement = direction * self.move_speed * dt
                self.physics_node.setPos(self.physics_node.getPos() + movement)
                
                # Update rotation to face movement direction
                heading = math.degrees(math.atan2(-direction.getX(), direction.getY()))
                self.physics_node.setH(heading)
    
    def has_line_of_sight(self):
        """Check if enemy has line of sight to player"""
        if not hasattr(self.base, 'player'):
            return False
        
        # Get direction to player
        direction = self.get_direction_to_player()
        start_pos = self.physics_node.getPos() + Vec3(0, 0, 1)  # Raise start position to eye level
        end_pos = self.base.player.physics_node.getPos() + Vec3(0, 0, 1)  # Aim at player's eye level
        
        # Perform raycast using bullet physics - check against both terrain and player
        result = self.base.collision_system.world.rayTestClosest(
            start_pos,
            end_pos,
            self.base.collision_system.MASK_TERRAIN | self.base.collision_system.MASK_PLAYER
        )
        
        if result.hasHit():
            hit_node = result.getNode()
            # If we hit the player, that's a valid line of sight
            if hit_node and hit_node.hasPythonTag('owner'):
                target = hit_node.getPythonTag('owner')
                if target == self.base.player:
                    print("LOS check - Direct hit on player")
                    return True
            
            # If we hit something else, check if it's closer than the player
            hit_dist = (result.getHitPos() - start_pos).length()
            player_dist = (end_pos - start_pos).length()
            
            # Debug print
            print(f"LOS check - Hit dist: {hit_dist:.1f}, Player dist: {player_dist:.1f}")
            
            # Return true if the player is closer than the obstacle
            return hit_dist >= player_dist
        
        # If no obstacles hit, we have line of sight
        print("LOS check - No obstacles hit")
        return True
    
    # FSM States
    def enterIdle(self):
        """Enter idle state"""
        self.actor.setColor(0.8, 0.2, 0.2, 1)  # Red color
    
    def exitIdle(self):
        pass
    
    def enterChase(self):
        """Enter chase state"""
        self.actor.setColor(1, 0.4, 0, 1)  # Orange color
    
    def exitChase(self):
        pass
    
    def enterAttack(self):
        """Enter attack state"""
        self.actor.setColor(1, 0, 0, 1)  # Bright red color
        self.perform_attack()
    
    def exitAttack(self):
        pass
    
    def cleanup(self):
        """Clean up resources"""
        self.base.taskMgr.remove("enemy_update")
        if self.health_bar:
            self.health_bar.destroy()
        if self.actor:
            self.actor.removeNode()
        if self.physics_node:
            self.physics_node.removeNode() 