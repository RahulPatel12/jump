from panda3d.core import (
    CollisionTraverser,
    CollisionHandlerPusher,
    CollisionHandlerQueue,
    CollisionNode,
    CollisionSphere,
    CollisionCapsule,
    CollisionRay,
    CollisionBox,
    CollisionPlane,
    Plane,
    Point3,
    Vec3,
    BitMask32
)

class CollisionSystem:
    # Collision masks
    MASK_PLAYER = BitMask32.bit(0)
    MASK_TERRAIN = BitMask32.bit(1)
    MASK_PLATFORM = BitMask32.bit(2)
    MASK_ENEMY = BitMask32.bit(3)
    MASK_COLLECTIBLE = BitMask32.bit(4)
    MASK_TRIGGER = BitMask32.bit(5)
    MASK_WALL = BitMask32.bit(6)
    MASK_CLIMBABLE = BitMask32.bit(7)
    
    def __init__(self, base):
        self.base = base
        
        # Create collision traverser
        self.traverser = CollisionTraverser("Main")
        self.traverser.setRespectPrevTransform(True)  # For continuous collision detection
        
        # Create collision handlers
        self.pusher = CollisionHandlerPusher()
        self.queue = CollisionHandlerQueue()
        
        # Enable debug visualization
        self.traverser.showCollisions(self.base.render)
    
    def setup_player_collisions(self, player):
        """Set up collision detection for the player"""
        # Player body collision (capsule for better 3D collision)
        body_node = CollisionNode("player_body")
        # Capsule from feet to head (radius 0.4, height 1.8)
        body_node.addSolid(CollisionCapsule(Point3(0, 0, 0), Point3(0, 0, 1.8), 0.4))
        body_node.setFromCollideMask(self.MASK_TERRAIN | self.MASK_PLATFORM | self.MASK_WALL)
        body_node.setIntoCollideMask(BitMask32.allOff())
        
        body_np = player.actor.attachNewNode(body_node)
        self.pusher.addCollider(body_np, player.actor)
        self.traverser.addCollider(body_np, self.pusher)
        
        # Ground ray for checking if player is on ground
        ray_node = CollisionNode("player_ground_ray")
        ray_node.addSolid(CollisionRay(0, 0, 0.1, 0, 0, -1))  # Slightly above feet, pointing down
        ray_node.setFromCollideMask(self.MASK_TERRAIN | self.MASK_PLATFORM)
        ray_node.setIntoCollideMask(BitMask32.allOff())
        
        ray_np = player.actor.attachNewNode(ray_node)
        self.traverser.addCollider(ray_np, self.queue)
        
        # Store collision nodes
        player.collision_body = body_np
        player.ground_ray = ray_np
    
    def setup_platform(self, model, is_moving=False):
        """Set up collision for a platform"""
        bounds = model.getTightBounds()
        if bounds:
            min_point, max_point = bounds
            size = max_point - min_point
            center = (min_point + max_point) / 2
        else:
            size = Vec3(1, 1, 1)
            center = Point3(0, 0, 0)
        
        collision_node = CollisionNode("platform")
        collision_node.addSolid(CollisionBox(center, size.x/2, size.y/2, size.z/2))
        
        collision_node.setFromCollideMask(BitMask32.allOff())
        collision_node.setIntoCollideMask(self.MASK_TERRAIN if not is_moving else self.MASK_PLATFORM)
        
        collision_np = model.attachNewNode(collision_node)
        return collision_np
    
    def setup_climbable_wall(self, model):
        """Set up collision for a climbable wall"""
        bounds = model.getTightBounds()
        if bounds:
            min_point, max_point = bounds
            size = max_point - min_point
            center = (min_point + max_point) / 2
        else:
            size = Vec3(1, 1, 1)
            center = Point3(0, 0, 0)
        
        collision_node = CollisionNode("climbable_wall")
        collision_node.addSolid(CollisionBox(center, size.x/2, size.y/2, size.z/2))
        
        collision_node.setFromCollideMask(BitMask32.allOff())
        collision_node.setIntoCollideMask(self.MASK_WALL | self.MASK_CLIMBABLE)
        
        collision_np = model.attachNewNode(collision_node)
        return collision_np
    
    def setup_trigger_volume(self, pos, size, name, callback):
        """Create a trigger volume that calls a function when entered"""
        trigger_node = CollisionNode(f"trigger_{name}")
        trigger_node.addSolid(CollisionBox(Point3(0, 0, 0), size.x/2, size.y/2, size.z/2))
        trigger_node.setFromCollideMask(BitMask32.allOff())
        trigger_node.setIntoCollideMask(self.MASK_TRIGGER)
        
        trigger_np = self.base.render.attachNewNode(trigger_node)
        trigger_np.setPos(pos)
        trigger_np.setPythonTag("callback", callback)
        
        return trigger_np
    
    def check_ground_collision(self, player):
        """Check if player is touching ground"""
        self.traverser.traverse(self.base.render)
        
        entries = []
        for i in range(self.queue.getNumEntries()):
            entry = self.queue.getEntry(i)
            if entry.getFromNode().name == "player_ground_ray":
                entries.append(entry)
        
        if entries:
            entries.sort(key=lambda x: x.getSurfacePoint(player.actor).getZ())
            contact = entries[0].getSurfacePoint(player.actor)
            return contact.getZ() <= 0.1  # Check if point is close enough to consider on ground
        
        return False
    
    def check_wall_collision(self, player):
        """Check if player is touching a climbable wall"""
        self.traverser.traverse(self.base.render)
        
        for i in range(self.queue.getNumEntries()):
            entry = self.queue.getEntry(i)
            if entry.getFromNode().name == "player_wall_ray":
                if entry.getIntoNode().getIntoCollideMask().hasBit(self.MASK_CLIMBABLE.getLowestOnBit()):
                    return True
        
        return False
    
    def cleanup(self):
        """Clean up collision system"""
        self.traverser.clearColliders() 