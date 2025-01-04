"""Common UI utilities and constants used across UI components"""
from direct.gui.DirectGui import DGG
from panda3d.core import TextNode

# Text alignments (using TextNode constants)
TEXT_ALIGN_CENTER = TextNode.ACenter
TEXT_ALIGN_LEFT = TextNode.ALeft
TEXT_ALIGN_RIGHT = TextNode.ARight

# Common colors
COLOR_WHITE = (1, 1, 1, 1)
COLOR_BLACK = (0, 0, 0, 1)
COLOR_TRANSPARENT = (0, 0, 0, 0)
COLOR_BUTTON = (0.2, 0.2, 0.2, 0.8)
COLOR_BUTTON_HOVER = (0.3, 0.3, 0.3, 0.8)
COLOR_DISABLED = (0.1, 0.1, 0.1, 0.8)
COLOR_TEXT_DISABLED = (0.5, 0.5, 0.5, 1)

# Common button properties
BUTTON_DEFAULTS = {
    'frameSize': (-0.4, 0.4, -0.07, 0.07),
    'text_scale': 0.07,
    'relief': DGG.FLAT,
    'frameColor': COLOR_BUTTON,
    'text_fg': COLOR_WHITE,
    'pressEffect': True
}

def setup_text_properties():
    """Setup text properties for alignment"""
    # Center alignment
    center = TextProperties()
    center.setAlignment(TextProperties.ACenter)
    TextPropertiesManager.getGlobalPtr().setProperties('center', center)
    
    # Left alignment
    left = TextProperties()
    left.setAlignment(TextProperties.ALeft)
    TextPropertiesManager.getGlobalPtr().setProperties('left', left)
    
    # Right alignment
    right = TextProperties()
    right.setAlignment(TextProperties.ARight)
    TextPropertiesManager.getGlobalPtr().setProperties('right', right) 