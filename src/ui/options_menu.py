from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectLabel,
    DirectSlider,
    DirectOptionMenu,
    DGG
)
from panda3d.core import TextNode, WindowProperties
from systems.settings import Settings

class OptionsMenu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.base = game_manager.base
        self.settings = Settings()  # Initialize settings
        
        # Create main background frame
        self.frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.15, 0.95),  # Slightly more opaque
            frameSize=(-0.6, 0.6, -0.7, 0.7),  # More compact size
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        
        # Make sure frame is visible during setup
        self.frame.show()
        
        # Create sections
        self.create_audio_section()
        self.create_graphics_section()
        self.create_controls_section()
        
        # Title
        self.title = DirectLabel(
            text="Options",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.6),
            parent=self.frame
        )
        
        # Back button
        self.back_button = DirectButton(
            text="Back",
            text_scale=0.04,
            text_pos=(0, -0.01),
            frameSize=(-0.1, 0.1, -0.04, 0.04),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(-0.5, 0, 0.6),
            parent=self.frame,
            command=self.on_back
        )
        self.back_button.bind(DGG.ENTER, self.on_button_hover, [self.back_button])
        self.back_button.bind(DGG.EXIT, self.on_button_exit, [self.back_button])
        
        # Save button
        self.save_button = DirectButton(
            text="Save Changes",
            text_scale=0.04,
            text_pos=(0, -0.01),
            frameSize=(-0.15, 0.15, -0.04, 0.04),
            frameColor=(0.2, 0.6, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0, 0, -0.6),
            parent=self.frame,
            command=self.save_settings
        )
        self.save_button.bind(DGG.ENTER, self.on_button_hover, [self.save_button])
        self.save_button.bind(DGG.EXIT, self.on_button_exit, [self.save_button])
        
        # Set up frame properties
        self.frame.setBin('gui-popup', 0)
        
        # Show the menu
        self.show()
    
    def create_audio_section(self):
        """Create audio settings section"""
        # Section title
        DirectLabel(
            text="Audio",
            text_scale=0.06,
            text_fg=(0.8, 0.8, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, 0.4),
            parent=self.frame
        )
        
        # Master volume slider
        DirectLabel(
            text="Master Volume",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.45, 0, 0.3),
            parent=self.frame
        )
        self.master_volume = DirectSlider(
            range=(0, 100),
            value=self.settings.get_master_volume() * 100,
            pageSize=10,
            frameSize=(-0.3, 0.3, -0.015, 0.015),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            thumb_frameColor=(0.5, 0.5, 0.5, 0.8),
            pos=(0.1, 0, 0.3),
            scale=0.7,
            parent=self.frame,
            command=self.on_volume_change
        )
        
        # Sound effects volume slider
        DirectLabel(
            text="Sound Effects",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.45, 0, 0.2),
            parent=self.frame
        )
        self.sfx_volume = DirectSlider(
            range=(0, 100),
            value=self.settings.get_sfx_volume() * 100,
            pageSize=10,
            frameSize=(-0.3, 0.3, -0.015, 0.015),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            thumb_frameColor=(0.5, 0.5, 0.5, 0.8),
            pos=(0.1, 0, 0.2),
            scale=0.7,
            parent=self.frame,
            command=self.on_sfx_change
        )
        
        # Music volume slider
        DirectLabel(
            text="Music",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.45, 0, 0.1),
            parent=self.frame
        )
        self.music_volume = DirectSlider(
            range=(0, 100),
            value=self.settings.get_music_volume() * 100,
            pageSize=10,
            frameSize=(-0.3, 0.3, -0.015, 0.015),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            thumb_frameColor=(0.5, 0.5, 0.5, 0.8),
            pos=(0.1, 0, 0.1),
            scale=0.7,
            parent=self.frame,
            command=self.on_music_change
        )
    
    def create_graphics_section(self):
        """Create graphics settings section"""
        # Section title
        DirectLabel(
            text="Graphics",
            text_scale=0.06,
            text_fg=(0.8, 0.8, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, -0.1),
            parent=self.frame
        )
        
        # Resolution dropdown
        DirectLabel(
            text="Resolution",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.45, 0, -0.2),
            parent=self.frame
        )
        
        # Get current resolution
        current_res = self.settings.get_resolution()
        current_res_str = f"{current_res[0]}x{current_res[1]}"
        
        self.resolution_menu = DirectOptionMenu(
            text_scale=0.04,
            frameSize=(-0.2, 0.2, -0.04, 0.04),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            highlightColor=(0.4, 0.4, 0.4, 0.8),
            pos=(0.1, 0, -0.2),
            items=['1920x1080', '1600x900', '1280x720'],
            initialitem=['1920x1080', '1600x900', '1280x720'].index(current_res_str),
            command=self.on_resolution_change,
            parent=self.frame
        )
        
        # Fullscreen toggle
        DirectLabel(
            text="Fullscreen",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.45, 0, -0.3),
            parent=self.frame
        )
        
        is_fullscreen = self.settings.get_fullscreen()
        self.fullscreen_button = DirectButton(
            text="On" if is_fullscreen else "Off",
            text_scale=0.04,
            text_pos=(0, -0.01),
            frameSize=(-0.1, 0.1, -0.04, 0.04),
            frameColor=(0.2, 0.6, 0.2, 0.8) if is_fullscreen else (0.6, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0.1, 0, -0.3),
            parent=self.frame,
            command=self.toggle_fullscreen
        )
    
    def create_controls_section(self):
        """Create controls settings section"""
        # Section title
        DirectLabel(
            text="Controls",
            text_scale=0.06,
            text_fg=(0.8, 0.8, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, -0.45),
            parent=self.frame
        )
        
        # Mouse sensitivity slider
        DirectLabel(
            text="Mouse Sensitivity",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            pos=(-0.45, 0, -0.5),
            parent=self.frame
        )
        
        try:
            current_sensitivity = self.settings.get_setting("controls", "mouse_sensitivity")
        except KeyError:
            current_sensitivity = 5
        
        self.sensitivity = DirectSlider(
            range=(1, 10),
            value=current_sensitivity,
            pageSize=1,
            frameSize=(-0.3, 0.3, -0.015, 0.015),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            thumb_frameColor=(0.5, 0.5, 0.5, 0.8),
            pos=(0.1, 0, -0.5),
            scale=0.7,
            parent=self.frame,
            command=self.on_sensitivity_change
        )
    
    def on_volume_change(self):
        """Handle master volume change"""
        volume = self.master_volume['value'] / 100
        self.settings.set_setting("audio", "master_volume", volume)
    
    def on_sfx_change(self):
        """Handle sound effects volume change"""
        volume = self.sfx_volume['value'] / 100
        self.settings.set_setting("audio", "sfx_volume", volume)
    
    def on_music_change(self):
        """Handle music volume change"""
        volume = self.music_volume['value'] / 100
        self.settings.set_setting("audio", "music_volume", volume)
    
    def on_resolution_change(self, resolution):
        """Handle resolution change"""
        width, height = map(int, resolution.split('x'))
        self.settings.set_setting("video", "resolution", (width, height))
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        is_fullscreen = self.fullscreen_button['text'] == "On"
        self.fullscreen_button['text'] = "Off" if is_fullscreen else "On"
        self.fullscreen_button['frameColor'] = (0.6, 0.2, 0.2, 0.8) if is_fullscreen else (0.2, 0.6, 0.2, 0.8)
        self.settings.set_setting("video", "fullscreen", not is_fullscreen)
    
    def on_sensitivity_change(self):
        """Handle mouse sensitivity change"""
        sensitivity = self.sensitivity['value']
        self.settings.set_setting("controls", "mouse_sensitivity", sensitivity)
    
    def save_settings(self):
        """Save all settings"""
        self.settings.save_settings()
        # Apply settings that need immediate effect
        self.apply_video_settings()
        self.hide()
        self.game_manager.request('MainMenu')
    
    def apply_video_settings(self):
        """Apply video settings immediately"""
        props = self.base.win.getProperties()
        resolution = self.settings.get_resolution()
        is_fullscreen = self.settings.get_fullscreen()
        
        wp = WindowProperties()
        wp.setSize(resolution[0], resolution[1])
        wp.setFullscreen(is_fullscreen)
        self.base.win.requestProperties(wp)
    
    def on_button_hover(self, button, event):
        """Handle button hover effect"""
        orig_color = button['frameColor']
        button['frameColor'] = (
            min(orig_color[0] + 0.1, 1.0),
            min(orig_color[1] + 0.1, 1.0),
            min(orig_color[2] + 0.1, 1.0),
            orig_color[3]
        )
    
    def on_button_exit(self, button, event):
        """Handle button exit effect"""
        orig_color = button['frameColor']
        button['frameColor'] = (
            max(orig_color[0] - 0.1, 0.0),
            max(orig_color[1] - 0.1, 0.0),
            max(orig_color[2] - 0.1, 0.0),
            orig_color[3]
        )
    
    def on_back(self):
        """Handle back button click"""
        self.hide()
        self.game_manager.request('MainMenu')
    
    def show(self):
        """Show the options menu"""
        self.frame.show()
        # Make sure it's in front of other UI elements
        self.frame.setBin('gui-popup', 0)
        self.frame.reparentTo(self.base.aspect2d)
    
    def hide(self):
        """Hide the options menu"""
        self.frame.hide()
        # Detach from scene to ensure it's fully hidden
        self.frame.detachNode()
    
    def cleanup(self):
        """Clean up resources"""
        self.frame.destroy()
