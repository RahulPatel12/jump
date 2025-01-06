from direct.gui.DirectGui import DirectWaitBar, DirectLabel, DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from direct.task.Task import Task
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import TextNode

class HUD:
    def __init__(self, base):
        self.base = base
        
        # Initialize stopwatch variables
        self.stopwatch_running = False
        self.start_time = 0
        self.elapsed_time = 0
        
        # Create health bar in top left
        self.health_bar = DirectWaitBar(
            text="",  # We'll use a separate label for the text
            frameSize=(-0.8, 0.8, -0.08, 0.08),
            barColor=(0.2, 0.8, 0.2, 1),  # Green color
            frameColor=(0.2, 0.2, 0.2, 0.8),
            pos=(-0.9, 0, 0.9),  # Top left position
            scale=0.3,
            value=100,
            range=100
        )
        
        # Add health text label above health bar
        self.health_text = OnscreenText(
            text="100/100",
            pos=(-0.9, 0.95),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Add lives counter in top right
        self.lives_text = OnscreenText(
            text="Lives: 3",
            pos=(0.9, 0.9),  # Top right position
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ARight,
            mayChange=True
        )
        
        # Add stopwatch in bottom left
        self.stopwatch_text = OnscreenText(
            text="Time: 0:00.00",
            pos=(-0.9, -0.9),  # Bottom left position
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Add control tooltips in bottom right
        tooltips = [
            "WASD - Move",
            "SPACE - Jump",
            "E - Fire Mode",
            "LEFT CLICK - Shoot",
            "ESC - Pause",
        ]
        
        # Create a frame for tooltips
        self.tooltip_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.7),
            frameSize=(-0.3, 0.3, -0.25, 0.25),
            pos=(0.85, 0, -0.7),  # Bottom right position
            scale=0.8
        )
        
        # Add tooltip text
        self.tooltips = []
        for i, tip in enumerate(tooltips):
            tooltip = OnscreenText(
                text=tip,
                pos=(0, 0.15 - i * 0.07),  # Stack tooltips vertically
                scale=0.05,
                fg=(1, 1, 1, 1),
                align=TextNode.ACenter,
                mayChange=False,
                parent=self.tooltip_frame
            )
            self.tooltips.append(tooltip)
        
        # Add update task for stopwatch
        taskMgr.add(self.update_stopwatch, "stopwatch_task")
    
    def update_health(self, current_health, max_health):
        """Update health bar and text"""
        self.health_bar['value'] = current_health
        self.health_text.setText(f"{int(current_health)}/{max_health}")
        
        # Update color based on health percentage
        health_percent = current_health / max_health
        if health_percent > 0.6:
            self.health_bar['barColor'] = (0.2, 0.8, 0.2, 1)  # Green
        elif health_percent > 0.3:
            self.health_bar['barColor'] = (0.8, 0.8, 0.2, 1)  # Yellow
        else:
            self.health_bar['barColor'] = (0.8, 0.2, 0.2, 1)  # Red
    
    def update_lives(self, lives):
        """Update lives counter"""
        self.lives_text.setText(f"Lives: {lives}")
    
    def start_stopwatch(self):
        """Start the stopwatch"""
        print("Starting stopwatch")  # Debug print
        self.stopwatch_running = True
        self.start_time = globalClock.getRealTime()
        self.elapsed_time = 0
    
    def stop_stopwatch(self):
        """Stop the stopwatch"""
        if self.stopwatch_running:
            print("Stopping stopwatch")  # Debug print
            self.stopwatch_running = False
            self.elapsed_time = globalClock.getRealTime() - self.start_time
            print(f"Final time: {self.elapsed_time:.2f} seconds")  # Debug print
    
    def get_elapsed_time(self):
        """Get the elapsed time in seconds"""
        if self.stopwatch_running:
            return globalClock.getRealTime() - self.start_time
        return self.elapsed_time
    
    def update_stopwatch(self, task):
        """Update stopwatch display"""
        if self.stopwatch_running:
            elapsed = self.get_elapsed_time()
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            self.stopwatch_text.setText(f"Time: {minutes}:{seconds:05.2f}")
            print(f"Stopwatch update: {minutes}:{seconds:05.2f}")  # Debug print
        return Task.cont
    
    def cleanup(self):
        """Clean up HUD elements"""
        self.health_bar.destroy()
        self.health_text.destroy()
        self.lives_text.destroy()
        self.stopwatch_text.destroy()
        self.tooltip_frame.destroy()
        for tooltip in self.tooltips:
            tooltip.destroy()
        taskMgr.remove("stopwatch_task")
