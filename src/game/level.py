from panda3d.core import Point3, Vec3
from game.enemy import Enemy
import json
import os

class Level:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        self.collision_system = game_manager.collision_system
        self.combat_system = game_manager.combat_system
        
        self.platforms = {}  # Dictionary to store platforms by ID
        self.enemies = []
        self.spawn_point = Point3(0, 0, 2)  # Default spawn point
        self.current_checkpoint = None
        self.checkpoints = {}  # Dictionary to store checkpoints
        self.victory_pad = None
        self.victory_trigger_height = None
        
        # Level bounds
        self.bounds_min = Point3(-15, -15, -10)
        self.bounds_max = Point3(15, 35, 25)
    
    def load_level(self, level_number):
        """Load a level from the levels directory"""
        try:
            # Get the absolute path to the level file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            level_path = os.path.join(base_dir, "assets", "levels", f"level_{level_number}.json")
            
            print(f"Loading level from: {level_path}")  # Debug print
            
            if not os.path.exists(level_path):
                print(f"Level file not found: {level_path}")
                return False
            
            with open(level_path, "r") as f:
                level_data = json.load(f)
            
            # Load spawn point
            if "spawn_point" in level_data:
                sp = level_data["spawn_point"]
                self.spawn_point = Point3(sp[0], sp[1], sp[2])
            
            # Load level bounds
            if "level_bounds" in level_data:
                bounds = level_data["level_bounds"]
                self.bounds_min = Point3(*bounds["min"])
                self.bounds_max = Point3(*bounds["max"])
            
            # Load platforms
            if "platforms" in level_data:
                for platform in level_data["platforms"]:
                    # Create platform model (for now using a scaled cube)
                    platform_model = self.base.loader.loadModel("models/box")
                    if not platform_model:
                        print("Failed to load platform model")
                        continue
                        
                    platform_model.reparentTo(self.base.render)
                    
                    # Set position
                    pos = platform["position"]
                    platform_model.setPos(pos[0], pos[1], pos[2])
                    
                    # Set scale
                    scale = platform.get("scale", [2, 2, 0.5])
                    platform_model.setScale(scale[0], scale[1], scale[2])
                    
                    # Set color
                    color = platform.get("color", [0.5, 0.5, 0.5, 1])
                    platform_model.setColor(*color)
                    
                    # Create collision shape
                    self.collision_system.make_collision_from_model(platform_model, mass=0)
                    
                    # Store platform by ID if it has one
                    if "id" in platform:
                        self.platforms[platform["id"]] = platform_model
                    
                    # Special handling for checkpoint and victory platforms
                    if platform.get("type") == "checkpoint":
                        self.checkpoints[platform["id"]] = platform_model
                    elif platform.get("type") == "victory":
                        self.victory_pad = platform_model
            
            # Load checkpoints data
            if "checkpoints" in level_data:
                for checkpoint in level_data["checkpoints"]:
                    if checkpoint["id"] in self.checkpoints:
                        spawn = checkpoint["spawn_point"]
                        self.checkpoints[checkpoint["id"]] = {
                            "model": self.checkpoints[checkpoint["id"]],
                            "spawn_point": Point3(spawn[0], spawn[1], spawn[2])
                        }
            
            # Load victory conditions
            if "victory" in level_data:
                self.victory_trigger_height = level_data["victory"]["trigger_height"]
            
            # Load enemies
            if "enemy_spawns" in level_data:
                for spawn in level_data["enemy_spawns"]:
                    pos = spawn["position"]
                    enemy_type = spawn.get("type", "basic")
                    
                    # Create enemy at spawn point
                    enemy = Enemy(
                        self.base,
                        self.collision_system,
                        self.combat_system,
                        Point3(pos[0], pos[1], pos[2])
                    )
                    self.enemies.append(enemy)
            
            print(f"Successfully loaded level {level_number}")  # Debug print
            return True
            
        except Exception as e:
            print(f"Error loading level {level_number}: {e}")
            import traceback
            traceback.print_exc()  # Print the full error traceback
            return False
    
    def check_victory(self, player_pos):
        """Check if player has reached victory conditions"""
        if self.victory_pad and self.victory_trigger_height:
            if player_pos.getZ() >= self.victory_trigger_height:
                pad_pos = self.victory_pad.getPos()
                # Check if player is above victory pad (with some tolerance)
                if (abs(player_pos.getX() - pad_pos.getX()) < 2 and 
                    abs(player_pos.getY() - pad_pos.getY()) < 2):
                    return True
        return False
    
    def check_checkpoint(self, player_pos):
        """Check if player has reached a new checkpoint"""
        for checkpoint_id, checkpoint in self.checkpoints.items():
            if isinstance(checkpoint, dict):  # New format with spawn point
                checkpoint_model = checkpoint["model"]
                checkpoint_pos = checkpoint_model.getPos()
                # Check if player is on checkpoint platform (with some tolerance)
                if (abs(player_pos.getX() - checkpoint_pos.getX()) < 2 and 
                    abs(player_pos.getY() - checkpoint_pos.getY()) < 2 and
                    abs(player_pos.getZ() - checkpoint_pos.getZ()) < 1):
                    if self.current_checkpoint != checkpoint_id:
                        self.current_checkpoint = checkpoint_id
                        return checkpoint["spawn_point"]
        return None
    
    def get_current_spawn_point(self):
        """Get the current spawn point (checkpoint or initial)"""
        if self.current_checkpoint and self.current_checkpoint in self.checkpoints:
            return self.checkpoints[self.current_checkpoint]["spawn_point"]
        return self.spawn_point
    
    def cleanup(self):
        """Remove all platforms and clean up the level"""
        for platform in self.platforms.values():
            platform.removeNode()
        self.platforms.clear()
        self.checkpoints.clear()
        self.victory_pad = None
        
        for enemy in self.enemies:
            enemy.cleanup()
        self.enemies.clear() 