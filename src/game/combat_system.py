from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    Point3, Vec3, BitMask32, CollisionNode, CollisionRay, 
    CollisionHandlerQueue, CollisionTraverser, CardMaker, ColorBlendAttrib, Vec4
)
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval, LerpScaleInterval, Parallel, LerpColorScaleInterval
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.bullet import BulletRayHit, BulletClosestHitRayResult, BulletAllHitsRayResult

class CombatSystem(DirectObject):
    def __init__(self, base):
        super().__init__()
        self.base = base
        
        # Combat variables
        self.PLAYER_DAMAGE = 34  # 3 shots to kill (enemy has 100 health: 34 * 3 = 102)
        self.ENEMY_DAMAGE = 9    # 12 shots to kill (player has 100 health: 9 * 12 = 108)
        self.KNOCKBACK_FORCE = 10
        
        # Cooldowns
        self.player_shoot_cooldown = 0.5  # Time between shots
        self.enemy_shoot_cooldown = 1.0
        self.player_shoot_timer = 0
        self.enemy_shoot_timers = {}  # Dictionary to track each enemy's cooldown
        
        # Visual effects
        self.bullet_model = None
        try:
            # Create a simple sphere for bullets
            from panda3d.core import Point3, Vec3, NodePath
            from direct.showbase.ShowBase import ShowBase
            
            # Create main bullet trail
            cm = CardMaker('bullet_model')
            cm.setFrame(-0.2, 0.2, -1.2, 1.2)  # Even longer and wider trail
            bullet = self.base.render.attachNewNode(cm.generate())
            bullet.setBillboardPointEye()  # Always face camera
            bullet.setDepthWrite(False)  # Don't write to depth buffer for glow
            bullet.setTransparency(1)  # Enable transparency
            bullet.setTwoSided(True)  # Visible from both sides
            bullet.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))  # Additive blending for glow
            self.bullet_model = bullet
            self.bullet_model.detachNode()  # Store for later use
            
            # Create secondary glow trail
            cm2 = CardMaker('glow_model')
            cm2.setFrame(-0.4, 0.4, -1.5, 1.5)  # Even bigger trail for glow
            glow = self.base.render.attachNewNode(cm2.generate())
            glow.setBillboardPointEye()
            glow.setDepthWrite(False)
            glow.setTransparency(1)
            glow.setTwoSided(True)
            glow.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            self.glow_model = glow
            self.glow_model.detachNode()
        except Exception as e:
            print("Warning: Could not create bullet model:", str(e))
        
        # Add update task
        self.base.taskMgr.add(self.update, "gun_combat_update")
    
    def perform_raycast(self, start_pos, direction, is_player):
        """Perform a bullet raycast using Bullet physics"""
        # Get the physics world from the collision system
        world = self.base.collision_system.world
        
        # Create raycast parameters
        end_pos = start_pos + direction * 1000  # Long range
        
        # Set up proper collision masks
        if is_player:
            # Player bullets check against enemy and terrain
            mask = self.base.collision_system.MASK_ENEMY | self.base.collision_system.MASK_TERRAIN
        else:
            # Enemy bullets check against player and terrain
            mask = self.base.collision_system.MASK_PLAYER | self.base.collision_system.MASK_TERRAIN
        
        # Perform raycast
        result = world.rayTestClosest(
            start_pos,
            end_pos,
            mask
        )
        
        return result
    
    def create_bullet_effect(self, start_pos, end_pos, hit=False, is_player=True):
        """Create visual bullet effect"""
        if not self.bullet_model or not self.glow_model:
            return
            
        # Create main bullet trail
        bullet = self.bullet_model.copyTo(self.base.render)
        bullet.setPos(start_pos)
        
        # Create glow trail
        glow = self.glow_model.copyTo(self.base.render)
        glow.setPos(start_pos)
        
        # Set colors based on who shot (more intense colors)
        if is_player:
            bullet.setColor(0.4, 0.6, 1, 1.0)  # Brighter blue with full opacity
            glow.setColor(0.2, 0.4, 1, 0.6)    # Brighter blue glow
        else:
            bullet.setColor(1, 0.4, 0.4, 1.0)  # Brighter red with full opacity
            glow.setColor(1, 0.2, 0.2, 0.6)    # Brighter red glow
        
        # Create sequence to animate bullet and glow
        time = 0.3  # Slower bullet travel
        bullet_move = LerpPosInterval(bullet, time, end_pos, startPos=start_pos)
        glow_move = LerpPosInterval(glow, time, end_pos, startPos=start_pos)
        
        def cleanup():
            if not bullet.isEmpty():
                bullet.removeNode()
            if not glow.isEmpty():
                glow.removeNode()
        
        # If hit, add impact flash effect
        if hit:
            flash = self.bullet_model.copyTo(self.base.render)
            flash.setPos(end_pos)
            flash.setScale(0.8)  # Even bigger flash
            
            # Color flash based on who shot (more intense)
            if is_player:
                flash.setColor(0.5, 0.7, 1, 1)  # More intense blue
            else:
                flash.setColor(1, 0.5, 0.5, 1)  # More intense red
            
            def cleanup_flash():
                if not flash.isEmpty():
                    flash.removeNode()
            
            # Create more dramatic flash sequence
            flash_seq = Sequence(
                Parallel(
                    LerpScaleInterval(flash, 0.1, Vec3(1.5, 1.5, 1.5)),  # Bigger expansion
                    LerpColorScaleInterval(flash, 0.1, Vec4(1, 1, 1, 0), Vec4(1, 1, 1, 1))  # Fade out
                ),
                Func(cleanup_flash)
            )
            flash_seq.start()
        
        # Start bullet and glow sequence with fade out
        Sequence(
            Parallel(
                bullet_move,
                glow_move,
                LerpColorScaleInterval(bullet, time * 0.8, Vec4(1, 1, 1, 0), Vec4(1, 1, 1, 1)),  # Fade out bullet later
                LerpColorScaleInterval(glow, time, Vec4(1, 1, 1, 0), Vec4(1, 1, 1, 1))  # Full time glow fade
            ),
            Func(cleanup)
        ).start()
    
    def player_shoot(self, player):
        """Handle player shooting"""
        if self.player_shoot_timer <= 0:
            # Get camera direction for bullet trajectory
            cam_quat = player.get_camera_direction()
            direction = cam_quat.getForward()
            
            # Get start position
            start_pos = player.physics_node.getPos() + Vec3(0, 0, 0.5)  # Adjust height
            
            # Perform raycast
            result = self.perform_raycast(start_pos, direction, True)
            
            # Process hit
            hit = False
            hit_pos = None
            
            if result.hasHit():
                hit_pos = result.getHitPos()
                hit_node = result.getNode()
                
                if hit_node and hit_node.hasPythonTag('owner'):
                    target = hit_node.getPythonTag('owner')
                    if hasattr(target, 'take_damage'):
                        # Calculate knockback direction
                        knockback = direction * self.KNOCKBACK_FORCE
                        target.take_damage(self.PLAYER_DAMAGE, knockback)
                        hit = True
            
            # Create visual effect
            if hit_pos:
                self.create_bullet_effect(start_pos, hit_pos, hit, True)
            else:
                # If no hit, send bullet in direction of aim
                end_pos = start_pos + direction * 500
                self.create_bullet_effect(start_pos, end_pos, False, True)
            
            # Start cooldown
            self.player_shoot_timer = self.player_shoot_cooldown
            return True
        return False
    
    def enemy_shoot(self, enemy):
        """Handle enemy shooting"""
        if enemy not in self.enemy_shoot_timers:
            self.enemy_shoot_timers[enemy] = 0
            
        if self.enemy_shoot_timers[enemy] <= 0:
            if hasattr(self.base, 'player'):
                print("Enemy attempting to shoot at player")
                # Calculate direction to player
                enemy_pos = enemy.physics_node.getPos()
                player_pos = self.base.player.physics_node.getPos()
                direction = (player_pos - enemy_pos)
                direction.normalize()
                
                # Get start position (raised to match eye level)
                start_pos = enemy_pos + Vec3(0, 0, 1)  # Adjust height
                
                # Perform raycast
                result = self.perform_raycast(start_pos, direction, False)
                
                # Process hit
                hit = False
                hit_pos = None
                
                if result.hasHit():
                    print("Enemy raycast hit something")
                    hit_pos = result.getHitPos()
                    hit_node = result.getNode()
                    
                    if hit_node and hit_node.hasPythonTag('owner'):
                        print("Hit something with owner tag")
                        target = hit_node.getPythonTag('owner')
                        if target == self.base.player:  # Specifically check if we hit the player
                            print("Target is player, applying damage...")
                            # Calculate knockback
                            knockback = direction * self.KNOCKBACK_FORCE
                            target.take_damage(self.ENEMY_DAMAGE, knockback)
                            hit = True
                            print("Damage applied successfully")
                        else:
                            print(f"Hit something else with owner tag: {target}")
                    else:
                        print("Hit something without owner tag or no hit_node")
                else:
                    print("Enemy raycast missed")
                
                # Create visual effect
                if hit_pos:
                    self.create_bullet_effect(start_pos, hit_pos, hit, False)
                else:
                    # If no hit, send bullet in direction of aim
                    end_pos = start_pos + direction * 500
                    self.create_bullet_effect(start_pos, end_pos, False, False)
                
                # Start cooldown
                self.enemy_shoot_timers[enemy] = self.enemy_shoot_cooldown
                return True
        return False
    
    def update(self, task):
        """Update combat system"""
        dt = globalClock.getDt()
        
        # Update player cooldown
        if self.player_shoot_timer > 0:
            self.player_shoot_timer -= dt
        
        # Update enemy cooldowns
        for enemy in list(self.enemy_shoot_timers.keys()):
            if self.enemy_shoot_timers[enemy] > 0:
                self.enemy_shoot_timers[enemy] -= dt
        
        return task.cont
    
    def cleanup(self):
        """Clean up combat system"""
        self.base.taskMgr.remove("gun_combat_update")
        self.ignoreAll() 