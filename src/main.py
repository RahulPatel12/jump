#!/usr/bin/env python3

import os
import sys

# Add src directory to Python path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from panda3d.core import WindowProperties, loadPrcFileData, Point3, Vec3, BitMask32
from panda3d.core import TransparencyAttrib, Filename

# Configure Panda3D settings
loadPrcFileData("", """
    window-title Jump!
    win-size 1280 720
    framebuffer-multisample 1
    multisamples 2
    show-frame-rate-meter 1
    sync-video 1
    bullet-enable-contact-events #t
    model-path $MAIN_DIR/assets
""".replace("$MAIN_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.game_manager import GameManager
from game.collision import CollisionSystem
from game.combat_system import CombatSystem
from game.player import Player
from systems.settings import Settings
from systems.input_manager import InputManager
from systems.audio_manager import AudioManager
from game.level import Level

# Import UI components
from ui.main_menu import MainMenu
from ui.options_menu import OptionsMenu
from ui.level_select import LevelSelect
from ui.leaderboard_menu import LeaderboardMenu
from ui.pause_menu import PauseMenu
from ui.hud import HUD
from ui.name_input import NameInput

class Jump(ShowBase, FSM):
    def __init__(self):
        ShowBase.__init__(self)
        FSM.__init__(self, 'GameFSM')
        
        # Set base attribute for compatibility
        self.base = self
        
        # Set window properties
        self.set_window_properties()
        
        # Initialize game systems
        self.settings = Settings()
        self.input_manager = InputManager()
        self.audio_manager = AudioManager(self)
        
        # Create collision system
        self.collision_system = CollisionSystem(self)
        
        # Create combat system
        self.combat_system = CombatSystem(self)
        
        # Initialize UI containers
        self.current_menu = None
        self.hud = None
        
        # Player data
        self.player_name = None
        
        # Start with main menu
        self.request('MainMenu')
        
        # Bind the escape key to pause/unpause
        self.accept("escape", self.toggle_pause)
    
    def enterMainMenu(self):
        """Enter main menu state"""
        # Show cursor in menu
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        
        # Create and show main menu
        self.current_menu = MainMenu(self)
    
    def exitMainMenu(self):
        """Exit main menu state"""
        if self.current_menu:
            self.current_menu.cleanup()
            self.current_menu = None
    
    def enterNameInput(self):
        """Enter name input state"""
        self.current_menu = NameInput(self)
    
    def exitNameInput(self):
        """Exit name input state"""
        if self.current_menu:
            self.current_menu.cleanup()
            self.current_menu = None
    
    def enterLevelSelect(self):
        """Enter level select state"""
        # Ensure we have a player name before allowing level select
        if not self.player_name:
            self.request('NameInput')
            return
        self.current_menu = LevelSelect(self)
    
    def exitLevelSelect(self):
        """Exit level select state"""
        if self.current_menu:
            self.current_menu.cleanup()
            self.current_menu = None
    
    def enterOptions(self):
        """Enter options menu state"""
        # Show cursor in options menu
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        
        self.current_menu = OptionsMenu(self)
    
    def exitOptions(self):
        """Exit options menu state"""
        if self.current_menu:
            self.current_menu.cleanup()
            self.current_menu = None
    
    def enterLeaderboard(self):
        """Enter leaderboard state"""
        self.current_menu = LeaderboardMenu(self)
    
    def exitLeaderboard(self):
        """Exit leaderboard state"""
        if self.current_menu:
            self.current_menu.cleanup()
            self.current_menu = None
    
    def enterGame(self):
        """Enter gameplay state"""
        # Hide cursor and enable relative mouse mode for gameplay
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        
        # Load the arena model
        self.arena = self.loader.loadModel("../assets/models/arena_1.bam")
        self.arena.reparentTo(self.render)
        self.arena.setPos(0, 0, 0)
        
        # Create collision mesh for the arena
        self.collision_system.make_collision_from_model(self.arena, mass=0)
        
        # Create level
        self.level = Level(self)
        if not self.level.load_level(self.current_level_num):
            print("Failed to load level!")
            self.taskMgr.doMethodLater(0.1, lambda task: self.request('MainMenu'), 'delayed_menu_transition')
            return
        
        # Create player at level's spawn point
        self.player = Player(self, self.collision_system, self.combat_system)
        self.player.physics_node.setPos(self.level.spawn_point)
        
        # Create HUD
        self.hud = HUD(self)
        
        # Enable mouse control for gameplay
        self.player.enable_mouse_control()
    
    def exitGame(self):
        """Exit gameplay state"""
        if hasattr(self, 'player'):
            self.player.cleanup()
            del self.player
        
        if self.hud:
            self.hud.cleanup()
            self.hud = None
        
        if hasattr(self, 'arena'):
            self.arena.removeNode()
            del self.arena
    
    def enterPaused(self):
        """Enter paused state"""
        if hasattr(self, 'player'):
            self.player.disable_mouse_control()
        
        # Show cursor in pause menu
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        
        self.current_menu = PauseMenu(self)
    
    def exitPaused(self):
        """Exit paused state"""
        if self.current_menu:
            self.current_menu.cleanup()
            self.current_menu = None
        
        if hasattr(self, 'player'):
            self.player.enable_mouse_control()
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == 'Game':
            self.request('Paused')
        elif self.state == 'Paused':
            self.resume_game()
    
    def resume_game(self):
        """Resume the game from pause"""
        self.request('Game')
    
    def start_level(self, level_num):
        """Start a specific level"""
        self.current_level_num = level_num
        self.request('Game')
    
    def quit_to_menu(self):
        """Quit current game and return to main menu"""
        self.request('MainMenu')
    
    def quit_game(self):
        """Exit the game"""
        self.userExit()
    
    def set_window_properties(self):
        """Set initial window properties"""
        props = WindowProperties()
        props.setTitle("Jump!")
        props.setSize(1280, 720)
        self.win.requestProperties(props)

def main():
    app = Jump()
    app.run()

if __name__ == "__main__":
    main() 