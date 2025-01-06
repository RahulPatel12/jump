from panda3d.core import Point3, Vec3
from direct.showbase.MessengerGlobal import messenger
from direct.gui.DirectGui import DirectWaitBar
from .enemy import Enemy

class Boss(Enemy):
    def __init__(self, base, collision_system, combat_system, position):
        super().__init__(base, collision_system, combat_system, position)
        
        # Make boss bigger (2x size)
        self.actor.setScale(2, 2, 4)  # Double the size
        self.actor.setPos(-1, -1, -2)  # Adjust position to account for new size
        self.actor.setColor(0.8, 0.1, 0.1, 1)  # Darker red color
        
        # Enhanced combat variables
        self.health = 500  # More health
        self.max_health = 500
        self.attack_damage = 15  # 7 shots to kill player (assuming player has 100 health)
        self.attack_cooldown = 1.5  # Slightly faster attacks than regular enemy
        self.attack_range = 20.0  # Longer range
        self.detection_range = 30.0  # Detect player from further away
        
        # Enhanced movement
        self.move_speed = 4.0  # Slightly slower due to size
        self.min_distance = 8.0  # Keep more distance due to size
        
        # Adjust health bar for bigger size
        self.health_bar.destroy()  # Remove old health bar
        self.health_bar = DirectWaitBar(
            range=self.max_health,
            value=self.health,
            barColor=(0.8, 0.1, 0.1, 1),  # Dark red color
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.5, 0.5, -0.05, 0.05),
            pos=(0, 0, 4),  # Position above boss
            scale=1.0,  # Bigger health bar
            parent=self.physics_node
        )
        self.health_bar.setBillboardPointEye()
    
    def take_damage(self, amount, knockback=None):
        """Override to reduce knockback effect"""
        if knockback:
            knockback *= 0.5  # Reduce knockback due to size
        return super().take_damage(amount, knockback)
    
    def die(self):
        """Override to send boss-specific defeat message"""
        self.cleanup()
        messenger.send('boss_defeated', [self])  # Signal boss defeat to game manager
    
    def perform_attack(self):
        """Override to add boss-specific attack behavior"""
        if not self.is_attacking and self.attack_timer <= 0:
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown
            
            # Boss shoots multiple times in quick succession
            success = False
            for _ in range(3):  # Shoot 3 times
                shot_success = self.combat_system.enemy_shoot(self)
                success = success or shot_success
                
            return success
        return False
    
    def update(self, task):
        """Override to add boss-specific behavior"""
        dt = globalClock.getDt()
        
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
        
        # Boss specific behavior: Enrage at low health
        if self.health < self.max_health * 0.3:  # Below 30% health
            self.attack_cooldown = 1.0  # Attack faster when enraged
            self.move_speed = 6.0  # Move faster when enraged
            self.actor.setColor(1.0, 0, 0, 1)  # Bright red when enraged
        
        return super().update(task)  # Continue with normal enemy behavior 