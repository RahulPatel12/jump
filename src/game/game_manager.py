from direct.fsm.FSM import FSM
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath, Point3, WindowProperties
from game.collision import CollisionSystem

class GameManager(FSM, DirectObject):
    def __init__(self, base):
        FSM.__init__(self, 'GameManager')
        DirectObject.__init__(self)
        
        self.base = base
        self.current_level = None
        self.player = None
        self.collision_system = None
        
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
        from game.level import Level
        from game.player import Player
        from ui.hud import HUD
        
        # Create collision system
        self.collision_system = CollisionSystem(self.base)
        
        # Create level
        self.current_level = Level(self)
        
        # Create player
        self.player = Player(self.base, self.collision_system)
        
        # Create HUD
        self.hud = HUD(self)
        
        # Set initial objective
        if hasattr(self.current_level, 'objective'):
            self.hud.set_objective(self.current_level.objective)
        
        # Hide mouse cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        
        # Set up camera
        self.base.cam.setPos(0, -20, 10)  # Back and up from origin
        self.base.cam.lookAt(Point3(0, 0, 0))  # Look at origin
        
        # Bind pause key
        self.accept('escape', self.toggle_pause)
    
    def exitPlaying(self):
        # Cleanup level and player
        if self.current_level:
            self.current_level.cleanup()
            self.current_level = None
        
        if self.player:
            self.player.cleanup()
            self.player = None
        
        if hasattr(self, 'hud'):
            self.hud.cleanup()
            del self.hud
        
        # Cleanup collision system
        if self.collision_system:
            self.collision_system.cleanup()
            self.collision_system = None
        
        # Show mouse cursor
        props = WindowProperties()
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)
        
        # Unbind pause key
        self.ignore('escape')
    
    def enterPaused(self):
        from ui.pause_menu import PauseMenu
        from panda3d.core import WindowProperties
        
        self.pause_menu = PauseMenu(self)
        
        # Pause physics
        if self.current_level:
            self.current_level.pause_physics()
        
        # Show mouse cursor
        props = WindowProperties()
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)
        
        # Bind pause key to resume
        self.accept('escape', self.toggle_pause)
    
    def exitPaused(self):
        if hasattr(self, 'pause_menu'):
            self.pause_menu.cleanup()
            del self.pause_menu
        
        # Resume physics
        if self.current_level:
            self.current_level.resume_physics()
        
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
        # TODO: Implement game over state
        pass
    
    def exitGameOver(self):
        # TODO: Clean up game over state
        pass 