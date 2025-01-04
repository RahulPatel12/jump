from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3

class InputManager(DirectObject):
    def __init__(self):
        super().__init__()
        
        # Default key bindings
        self.key_map = {
            "move_forward": ["w", "arrow_up"],
            "move_backward": ["s", "arrow_down"],
            "move_left": ["a", "arrow_left"],
            "move_right": ["d", "arrow_right"],
            "jump": ["space"],
            "run": ["shift"],
            "attack": ["mouse1"],
            "block": ["mouse2"],
            "dodge": ["control"],
            "pause": ["escape"],
            "interact": ["e"],
        }
        
        # State of keys
        self.key_states = {}
        
        # Initialize all key states to False
        for action in self.key_map:
            self.key_states[action] = False
            
        # Set up input handlers
        self.setup_input_handlers()
    
    def setup_input_handlers(self):
        """Set up all input event handlers"""
        # Bind all keys
        for action, keys in self.key_map.items():
            for key in keys:
                self.accept(key, self.update_key_state, [action, True])
                self.accept(f"{key}-up", self.update_key_state, [action, False])
    
    def update_key_state(self, action, is_pressed):
        """Update the state of a key"""
        self.key_states[action] = is_pressed
    
    def is_action_pressed(self, action):
        """Check if an action's key is currently pressed"""
        return self.key_states.get(action, False)
    
    def get_movement_direction(self):
        """Get the current movement direction based on pressed keys"""
        direction = Vec3(0, 0, 0)
        
        if self.is_action_pressed("move_forward"):
            direction.y += 1
        if self.is_action_pressed("move_backward"):
            direction.y -= 1
        if self.is_action_pressed("move_left"):
            direction.x -= 1
        if self.is_action_pressed("move_right"):
            direction.x += 1
        
        # Normalize the direction vector if it's not zero
        if direction.length() > 0:
            direction.normalize()
        
        return direction
    
    def update_key_binding(self, action, new_keys):
        """Update the key binding for an action"""
        # Remove old bindings
        if action in self.key_map:
            for key in self.key_map[action]:
                self.ignore(key)
                self.ignore(f"{key}-up")
        
        # Set new binding
        self.key_map[action] = new_keys if isinstance(new_keys, list) else [new_keys]
        
        # Set up new handlers
        for key in self.key_map[action]:
            self.accept(key, self.update_key_state, [action, True])
            self.accept(f"{key}-up", self.update_key_state, [action, False])
    
    def get_key_binding(self, action):
        """Get the current key binding for an action"""
        return self.key_map.get(action, [])
    
    def cleanup(self):
        """Clean up input handlers"""
        self.ignoreAll() 