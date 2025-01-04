from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectSlider,
    DirectOptionMenu,
    DirectLabel,
    DGG,
    DirectScrolledFrame
)
from panda3d.core import TextNode

class OptionsMenu:
    def __init__(self, base, settings):
        self.base = base
        self.settings = settings
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = DirectLabel(
            text="Options",
            text_scale=0.1,
            text_pos=(0, -0.03),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.6),
            parent=self.frame
        )
        
        # Create tabs for different settings categories
        self.create_video_settings()
        self.create_audio_settings()
        self.create_control_settings()
        
        # Back button
        self.back_button = DirectButton(
            text="Back",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.1, 0.1, -0.05, 0.05),
            frameColor=(0.6, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(-0.6, 0, -0.7),
            parent=self.frame,
            command=self.on_back
        )
        
        # Initially hide the menu
        self.hide()
    
    def create_video_settings(self):
        """Create video settings controls"""
        # Video settings frame
        video_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.6, 0.6, -0.4, 0.4),
            pos=(-0.1, 0, 0.1),
            parent=self.frame
        )
        
        # Resolution dropdown
        resolutions = ["1280x720", "1920x1080", "2560x1440"]
        current_res = f"{self.settings.get_resolution()[0]}x{self.settings.get_resolution()[1]}"
        
        DirectLabel(
            text="Resolution:",
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, 0.3),
            parent=video_frame
        )
        
        DirectOptionMenu(
            text_scale=0.05,
            scale=0.7,
            initialitem=resolutions.index(current_res) if current_res in resolutions else 0,
            items=resolutions,
            highlightColor=(0.3, 0.3, 0.3, 1),
            pos=(0.1, 0, 0.3),
            command=self.on_resolution_change,
            parent=video_frame
        )
        
        # Fullscreen toggle
        DirectLabel(
            text="Fullscreen:",
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, 0.15),
            parent=video_frame
        )
        
        DirectButton(
            text="✓" if self.settings.get_fullscreen() else "✗",
            text_scale=0.05,
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            frameColor=(0.2, 0.6, 0.2, 0.8) if self.settings.get_fullscreen() else (0.6, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0.1, 0, 0.15),
            command=self.on_fullscreen_toggle,
            parent=video_frame
        )
        
        # Graphics quality dropdown
        qualities = ["low", "medium", "high"]
        current_quality = self.settings.get_graphics_quality()
        
        DirectLabel(
            text="Graphics Quality:",
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, 0),
            parent=video_frame
        )
        
        DirectOptionMenu(
            text_scale=0.05,
            scale=0.7,
            initialitem=qualities.index(current_quality),
            items=qualities,
            highlightColor=(0.3, 0.3, 0.3, 1),
            pos=(0.1, 0, 0),
            command=self.on_quality_change,
            parent=video_frame
        )
    
    def create_audio_settings(self):
        """Create audio settings controls"""
        # Audio settings frame
        audio_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.6, 0.6, -0.3, 0.3),
            pos=(-0.1, 0, -0.3),
            parent=self.frame
        )
        
        # Master volume slider
        DirectLabel(
            text="Master Volume:",
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, 0.2),
            parent=audio_frame
        )
        
        DirectSlider(
            scale=0.5,
            value=self.settings.get_master_volume(),
            range=(0, 1),
            pageSize=0.1,
            orientation=DGG.HORIZONTAL,
            command=self.on_master_volume_change,
            pos=(0.1, 0, 0.2),
            parent=audio_frame
        )
        
        # Music volume slider
        DirectLabel(
            text="Music Volume:",
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, 0.05),
            parent=audio_frame
        )
        
        DirectSlider(
            scale=0.5,
            value=self.settings.get_music_volume(),
            range=(0, 1),
            pageSize=0.1,
            orientation=DGG.HORIZONTAL,
            command=self.on_music_volume_change,
            pos=(0.1, 0, 0.05),
            parent=audio_frame
        )
        
        # SFX volume slider
        DirectLabel(
            text="SFX Volume:",
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, -0.1),
            parent=audio_frame
        )
        
        DirectSlider(
            scale=0.5,
            value=self.settings.get_sfx_volume(),
            range=(0, 1),
            pageSize=0.1,
            orientation=DGG.HORIZONTAL,
            command=self.on_sfx_volume_change,
            pos=(0.1, 0, -0.1),
            parent=audio_frame
        )
    
    def create_control_settings(self):
        """Create control settings interface"""
        # Controls frame
        controls_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.6, 0.6, -0.5, 0.5),
            pos=(-0.1, 0, -0.1),
            parent=self.frame
        )
        
        # Title
        DirectLabel(
            text="Controls",
            text_scale=0.06,
            text_pos=(0, -0.02),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.4),
            parent=controls_frame
        )
        
        # Create scrolled frame for control bindings
        bindings_frame = DirectScrolledFrame(
            frameSize=(-0.55, 0.55, -0.35, 0.35),
            canvasSize=(-0.5, 0.5, -0.8, 0.8),
            frameColor=(0.15, 0.15, 0.15, 0.8),
            scrollBarWidth=0.04,
            parent=controls_frame,
            pos=(0, 0, 0)
        )
        
        # Get current key bindings
        bindings = self.settings.get_key_bindings()
        
        # Create binding entries
        y_pos = 0.7
        self.binding_buttons = {}
        
        for action, keys in bindings.items():
            # Action label
            DirectLabel(
                text=action.replace('_', ' ').title() + ":",
                text_scale=0.05,
                text_align=TextNode.ALeft,
                text_fg=(1, 1, 1, 1),
                frameColor=(0, 0, 0, 0),
                pos=(-0.45, 0, y_pos),
                parent=bindings_frame.getCanvas()
            )
            
            # Key binding button
            key_text = " + ".join(keys)
            button = DirectButton(
                text=key_text,
                text_scale=0.05,
                text_pos=(0, -0.015),
                frameSize=(-0.2, 0.2, -0.03, 0.03),
                frameColor=(0.2, 0.2, 0.2, 0.8),
                text_fg=(1, 1, 1, 1),
                relief=DGG.FLAT,
                pos=(0.2, 0, y_pos),
                parent=bindings_frame.getCanvas(),
                command=self.start_key_binding,
                extraArgs=[action, button]
            )
            
            self.binding_buttons[action] = button
            y_pos -= 0.15
        
        # Reset controls button
        self.reset_controls_button = DirectButton(
            text="Reset to Defaults",
            text_scale=0.05,
            text_pos=(0, -0.015),
            frameSize=(-0.2, 0.2, -0.05, 0.05),
            frameColor=(0.6, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pos=(0, 0, -0.45),
            parent=controls_frame,
            command=self.reset_controls
        )
        
        # Add hover effect
        self.reset_controls_button.bind(DGG.ENTER, self.on_button_hover, [self.reset_controls_button, True])
        self.reset_controls_button.bind(DGG.EXIT, self.on_button_hover, [self.reset_controls_button, False])
    
    def start_key_binding(self, action, button):
        """Start listening for a new key binding"""
        button['text'] = "Press a key..."
        button['frameColor'] = (0.3, 0.3, 0.3, 0.8)
        
        # Store the current bindings
        self.current_binding_action = action
        self.current_binding_button = button
        
        # Start listening for key events
        self.accept_once('space', self.on_key_press, ['space'])
        self.accept_once('escape', self.on_key_press, ['escape'])
        self.accept_once('enter', self.on_key_press, ['enter'])
        self.accept_once('tab', self.on_key_press, ['tab'])
        self.accept_once('backspace', self.on_key_press, ['backspace'])
        self.accept_once('shift', self.on_key_press, ['shift'])
        self.accept_once('control', self.on_key_press, ['control'])
        self.accept_once('alt', self.on_key_press, ['alt'])
        
        # Accept letter keys
        for i in range(26):
            key = chr(ord('a') + i)
            self.accept_once(key, self.on_key_press, [key])
        
        # Accept number keys
        for i in range(10):
            key = str(i)
            self.accept_once(key, self.on_key_press, [key])
        
        # Accept arrow keys
        self.accept_once('arrow_up', self.on_key_press, ['arrow_up'])
        self.accept_once('arrow_down', self.on_key_press, ['arrow_down'])
        self.accept_once('arrow_left', self.on_key_press, ['arrow_left'])
        self.accept_once('arrow_right', self.on_key_press, ['arrow_right'])
        
        # Accept mouse buttons
        self.accept_once('mouse1', self.on_key_press, ['mouse1'])
        self.accept_once('mouse2', self.on_key_press, ['mouse2'])
        self.accept_once('mouse3', self.on_key_press, ['mouse3'])
    
    def on_key_press(self, key):
        """Handle key press for binding"""
        if hasattr(self, 'current_binding_action') and hasattr(self, 'current_binding_button'):
            # Update settings
            self.settings.set_setting("controls", self.current_binding_action, [key])
            
            # Update button text
            self.current_binding_button['text'] = key
            self.current_binding_button['frameColor'] = (0.2, 0.2, 0.2, 0.8)
            
            # Clear current binding state
            del self.current_binding_action
            del self.current_binding_button
            
            # Stop listening for keys
            self.ignore_all()
    
    def reset_controls(self):
        """Reset controls to default settings"""
        self.settings.reset_to_defaults("controls")
        
        # Update all binding buttons
        bindings = self.settings.get_key_bindings()
        for action, keys in bindings.items():
            if action in self.binding_buttons:
                self.binding_buttons[action]['text'] = " + ".join(keys)
    
    def on_button_hover(self, button, hover, event):
        """Handle button hover effects"""
        if hover:
            orig_color = button['frameColor']
            button['frameColor'] = (
                min(orig_color[0] + 0.1, 1.0),
                min(orig_color[1] + 0.1, 1.0),
                min(orig_color[2] + 0.1, 1.0),
                orig_color[3]
            )
        else:
            orig_color = button['frameColor']
            button['frameColor'] = (
                max(orig_color[0] - 0.1, 0.0),
                max(orig_color[1] - 0.1, 0.0),
                max(orig_color[2] - 0.1, 0.0),
                orig_color[3]
            )
    
    def on_resolution_change(self, resolution):
        """Handle resolution change"""
        width, height = map(int, resolution.split('x'))
        self.settings.set_setting("video", "resolution", (width, height))
        # TODO: Apply resolution change
    
    def on_fullscreen_toggle(self):
        """Handle fullscreen toggle"""
        current = self.settings.get_fullscreen()
        self.settings.set_setting("video", "fullscreen", not current)
        # TODO: Apply fullscreen change
    
    def on_quality_change(self, quality):
        """Handle graphics quality change"""
        self.settings.set_setting("video", "graphics_quality", quality)
        # TODO: Apply quality changes
    
    def on_master_volume_change(self):
        """Handle master volume change"""
        # TODO: Implement master volume control
        pass
    
    def on_music_volume_change(self, volume):
        """Handle music volume change"""
        self.settings.set_setting("audio", "music_volume", volume)
        # TODO: Apply volume change to audio manager
    
    def on_sfx_volume_change(self, volume):
        """Handle sound effects volume change"""
        self.settings.set_setting("audio", "sfx_volume", volume)
        # TODO: Apply volume change to audio manager
    
    def on_back(self):
        """Handle back button click"""
        self.hide()
        # TODO: Show main menu
        print("Back to main menu")
    
    def show(self):
        """Show the options menu"""
        self.frame.show()
    
    def hide(self):
        """Hide the options menu"""
        self.frame.hide()
