from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import ZUp
from panda3d.core import BitMask32, Point3, Vec3
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.bullet import BulletDebugNode

class CollisionSystem:
    # Collision masks
    MASK_PLAYER = BitMask32.bit(0)
    MASK_TERRAIN = BitMask32.bit(1)
    MASK_PLATFORM = BitMask32.bit(2)
    MASK_ENEMY = BitMask32.bit(3)
    MASK_COLLECTIBLE = BitMask32.bit(4)
    MASK_TRIGGER = BitMask32.bit(5)
    
    def __init__(self, base):
        self.base = base
        
        # Create Bullet world
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -75.0))
        
        # Enable debug visualization
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(True)
        debugNode.showNormals(True)
        
        debugNP = self.base.render.attachNewNode(debugNode)
        debugNP.show()
        
        self.world.setDebugNode(debugNode)
        
        # Add physics update task
        self.base.taskMgr.add(self.update, "physics_update")
    
    def setup_player(self, player):
        """Set up collision detection for the player"""
        # Create capsule shape for player
        shape = BulletCapsuleShape(0.5, 1.0, ZUp)  # radius, height, up-axis
        player_node = BulletCharacterControllerNode(shape, 0.4, 'Player')  # shape, step height, name
        player_np = self.base.render.attachNewNode(player_node)
        player_np.setPos(0, 0, 2)  # Start slightly above ground
        
        # Set specific collision mask for player (can collide with terrain, platforms, enemy bullets)
        player_np.setCollideMask(self.MASK_PLAYER | self.MASK_TERRAIN | self.MASK_PLATFORM)
        
        # Set up character controller properties
        player_node.setGravity(35.0)  # Reduced gravity for better jump control
        player_node.setMaxSlope(45.0)  # Maximum slope the player can climb (in degrees)
        player_node.setMaxJumpHeight(8.0)  # Increased max jump height
        player_node.setJumpSpeed(20.0)  # Set base jump speed
        player_node.setFallSpeed(45.0)  # Reduced fall speed for better control
        
        self.world.attachCharacter(player_np.node())
        return player_np
    
    def setup_enemy(self, enemy):
        """Set up collision detection for an enemy"""
        # Create capsule shape for enemy
        shape = BulletCapsuleShape(0.5, 1.0, ZUp)  # radius, height, up-axis
        enemy_node = BulletCharacterControllerNode(shape, 0.4, 'Enemy')  # shape, step height, name
        enemy_np = self.base.render.attachNewNode(enemy_node)
        
        # Set specific collision mask for enemy (can collide with terrain, platforms, player bullets)
        enemy_np.setCollideMask(self.MASK_ENEMY | self.MASK_TERRAIN | self.MASK_PLATFORM)
        
        self.world.attachCharacter(enemy_np.node())
        return enemy_np
    
    def make_collision_from_model(self, model, mass=0):
        """Create collision mesh from a 3D model"""
        # Create triangle mesh from model geometry
        mesh = BulletTriangleMesh()
        for np in model.findAllMatches('**/+GeomNode'):
            geom_node = np.node()
            for i in range(geom_node.getNumGeoms()):
                mesh.addGeom(geom_node.getGeom(i))
        
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        
        # Create rigid body
        body = BulletRigidBodyNode('model_collision')
        body_np = self.base.render.attachNewNode(body)
        body_np.node().addShape(shape)
        body_np.node().setMass(mass)
        body_np.node().setFriction(0.5)
        body_np.setPos(model.getPos())
        body_np.setHpr(model.getHpr())
        body_np.setScale(model.getScale())
        body_np.setCollideMask(BitMask32.allOn())
        
        self.world.attachRigidBody(body_np.node())
        return body_np
    
    def update(self, task):
        """Update physics simulation"""
        dt = globalClock.getDt()
        self.world.doPhysics(dt)
        return task.cont
    
    def cleanup(self):
        """Clean up physics world"""
        self.base.taskMgr.remove("physics_update")
        # Remove all bodies from the world
        for node in self.base.render.findAllMatches('**/+BulletRigidBodyNode'):
            self.world.removeRigidBody(node.node())
        for node in self.base.render.findAllMatches('**/+BulletCharacterControllerNode'):
            self.world.removeCharacter(node.node()) 