from direct.fsm.FSM import FSM
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath, Point3, WindowProperties, TextNode
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DGG
from game.collision import CollisionSystem
from game.combat_system import CombatSystem
from ui.game_over_screen import GameOverScreen
from game.player import Player
from game.level import Level
from ui.hud import HUD
from ui.pause_menu import PauseMenu

class GameManager(FSM, DirectObject):
    def __init__(self, base):
        FSM.__init__(self, 'GameManager')
        DirectObject.__init__(self)
        
        print("GameManager init with base type:", type(base))
        self.base = base
        self.current_level = None
        self.player = None
        self.collision_system = None
        self.combat_system = None
        
        # Set up initial camera position
        self.base.cam.setPos(0, -20, 10)  # Back and up from origin
        self.base.cam.lookAt(Point3(0, 0, 0))  # Look at origin
        
        # Initialize states
        self.defaultTransitions = {
            'MainMenu': ['LevelSelect', 'Options', 'Leaderboard'],
            'LevelSelect': ['Playing', 'MainMenu'],
            'Playing': ['Paused', 'MainMenu', 'GameOver'],
            'Paused': ['Playing', 'MainMenu', 'Options'],
            'Options': ['MainMenu', 'Paused'],
            'Leaderboard': ['MainMenu'],
            'GameOver': ['MainMenu', 'LevelSelect']
        }
        
        # Create systems
        self.collision_system = CollisionSystem(base)
        self.combat_system = CombatSystem(base)
        
        # Create player
        self.player = Player(base, self.collision_system, self.combat_system)
        
        # Create HUD
        self.hud = HUD(base)
        
        # Add update task
        self.base.taskMgr.add(self.update, "game_manager_update")
        
        # Listen for game over event
        self.accept('game_over', self.on_game_over)
    
    def update(self, task):
        """Update game state"""
        # Update HUD with player stats
        self.hud.update_health(self.player.health, self.player.max_health)
        self.hud.update_lives(self.player.lives)
        
        # Check for victory condition
        if self.current_level and self.player:
            if self.current_level.check_victory(self.player.physics_node.getPos()):
                print("Victory condition met - stopping stopwatch")  # Debug print
                self.hud.stop_stopwatch()
                # TODO: Save time to leaderboard
                self.request('MainMenu')
        
        return task.cont
    
    def enterMainMenu(self):
        from ui.main_menu import MainMenu
        self.main_menu = MainMenu(self)
    
    def exitMainMenu(self):
        if hasattr(self, 'main_menu'):
            self.main_menu.cleanup()
            del self.main_menu
    
    def enterLevelSelect(self):
        from ui.level_select import LevelSelect
        self.level_select = LevelSelect(self)
    
    def exitLevelSelect(self):
        if hasattr(self, 'level_select'):
            self.level_select.cleanup()
            del self.level_select
    
    def enterPlaying(self, level_name="level1"):
        """Enter the playing state with the specified level"""
        print("Entering playing state...")
        
        # Create collision system
        self.collision_system = CollisionSystem(self.base)
        print("Created collision system")
        
        # Create combat system
        self.combat_system = CombatSystem(self.base)
        print("Created combat system")
        
        # Create level
        self.current_level = Level(self)
        print("Created level")
        
        # Create player with combat system
        self.player = Player(self.base, self.collision_system, self.combat_system)
        print("Created player")
        
        # Create HUD with explicit ShowBase instance
        try:
            print("Base type:", type(self.base))
            print("Base aspect2d:", self.base.aspect2d)
            print("Base render2d:", self.base.render2d)
            self.hud = HUD(self.base)
            print("Created HUD successfully")
        except Exception as e:
            print("Error creating HUD:", str(e))
            import traceback
            traceback.print_exc()
        
        # Enable mouse control for player
        self.player.enable_mouse_control()
        print("Enabled mouse control")
        
        # Load the specified level
        print(f"Starting level {level_name}")
        level_num = int(level_name.replace("level", ""))
        if not self.current_level.load_level(level_num):
            print("Failed to load level!")
            # Schedule transition to main menu after a short delay
            self.base.taskMgr.doMethodLater(0.1, lambda task: self.request('MainMenu'), 'delayed_menu_transition')
            return
        
        # Set player spawn point and make invulnerable
        self.player.set_checkpoint(self.current_level.spawn_point)
        self.player.is_invulnerable = True
        self.player.invulnerability_timer = 3.0  # 3 seconds of invulnerability on level start
        self.player.respawn()
        print("Player spawned with 3 seconds of invulnerability")
        
        # Start the stopwatch
        print("Starting stopwatch for level")  # Debug print
        self.hud.start_stopwatch()
    
    def exitPlaying(self):
        """Exit the playing state"""
        # Stop the stopwatch if it's still running
        if hasattr(self, 'hud'):
            print("Stopping stopwatch on exit")  # Debug print
            self.hud.stop_stopwatch()
        
        if self.player:
            self.player.cleanup()
            self.player = None
        
        if hasattr(self, 'hud'):
            self.hud.cleanup()
            del self.hud
        
        if self.current_level:
            self.current_level.cleanup()
            self.current_level = None
        
        if self.combat_system:
            self.combat_system.cleanup()
            self.combat_system = None
        
        if self.collision_system:
            self.collision_system.cleanup()
            self.collision_system = None
    
    def enterPaused(self):
        """Enter paused state"""
        self.pause_menu = PauseMenu(self)
        
        # Disable mouse for game
        if self.player:
            self.player.disable_mouse_control()
    
    def exitPaused(self):
        if hasattr(self, 'pause_menu'):
            self.pause_menu.cleanup()
            del self.pause_menu
        
        # Hide mouse cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        
        # Unbind pause key
        self.ignore('escape')
    
    def toggle_pause(self):
        """Toggle between playing and paused states"""
        if self.state == 'Playing':
            self.request('Paused')
        elif self.state == 'Paused':
            self.request('Playing')
    
    def initialize(self):
        # Start with main menu
        self.request('MainMenu')
    
    def enterLeaderboard(self):
        from ui.leaderboard_menu import LeaderboardMenu
        self.leaderboard = LeaderboardMenu(self)
    
    def exitLeaderboard(self):
        if hasattr(self, 'leaderboard'):
            self.leaderboard.cleanup()
            del self.leaderboard
    
    def enterOptions(self):
        from ui.options_menu import OptionsMenu
        self.options_menu = OptionsMenu(self)
    
    def exitOptions(self):
        if hasattr(self, 'options_menu'):
            self.options_menu.cleanup()
            del self.options_menu
    
    def enterGameOver(self):
        """Enter game over state"""
        # Disable mouse control
        if self.player:
            self.player.disable_mouse_control()
        
        print("Entering game over state")
        self.game_over_screen = GameOverScreen(self)
    
    def exitGameOver(self):
        """Exit game over state"""
        if hasattr(self, 'game_over_screen'):
            self.game_over_screen.cleanup()
            del self.game_over_screen
    
    def restart_level(self):
        """Restart the current level"""
        print("Restarting level...")
        # Store current level name
        current_level = "level1"  # Default to level 1
        if self.current_level:
            current_level = f"level{self.current_level.level_number}"
        
        # Clean up current level
        self.exitPlaying()
        
        # Start fresh
        self.enterPlaying(current_level)
    
    def on_game_over(self):
        """Handle game over event"""
        print("Game over triggered")
        self.request('GameOver') 