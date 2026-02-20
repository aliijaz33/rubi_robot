
# tkinter is required for the on‑screen simulator. some Python builds (e.g.
# pyenv without tcl/tk) omit the `_tkinter` extension and will raise
# ModuleNotFoundError – those interpreters cannot run the GUI.  Providing a
# clear error message helps users switch to an appropriate environment.
try:
    import tkinter as tk
except ModuleNotFoundError as e:
    raise ImportError(
        "Tkinter is not available in this Python interpreter. "
        "Use a conda environment or a Python build with Tcl/Tk support."
    ) from e

import math
import time

class VisualMotorSimulator:
    """Tkinter-based visual motor simulator"""
    
    def __init__(self):
        self.left_speed = 0
        self.right_speed = 0
        self.left_dir = 1
        self.right_dir = 1
        self.running = True
        self.root = None
        
        print("🤖 Visual simulator initialized (waiting for GUI start...)")
        print("💡 Tip: Buttons will work once GUI opens")
        
    def start_gui(self):
        """Start the GUI (call this from main thread)"""
        self._create_gui()
        
    def _create_gui(self):
        """Create the tkinter GUI window"""
        self.root = tk.Tk()
        self.root.title("🤖 RUBI ROBOT - Visual Motor Simulator")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Configure style
        self.root.configure(bg='#2b2b2b')
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="RUBI ROBOT SIMULATOR", 
                        font=('Arial', 24, 'bold'), 
                        fg='#00ff00', bg='#2b2b2b')
        title.pack(pady=10)
        
        # Canvas for robot drawing
        self.canvas = tk.Canvas(main_frame, width=600, height=300, 
                                bg='#1a1a1a', highlightthickness=2,
                                highlightbackground='#00ff00')
        self.canvas.pack(pady=20)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#2b2b2b')
        status_frame.pack(fill='x', pady=10)
        
        # Mode display
        self.mode_label = tk.Label(status_frame, text="MODE: STOPPED", 
                                   font=('Arial', 16, 'bold'),
                                   fg='#ffaa00', bg='#2b2b2b')
        self.mode_label.pack()
        
        # Motor speed frames
        motors_frame = tk.Frame(main_frame, bg='#2b2b2b')
        motors_frame.pack(fill='x', pady=20)
        
        # Left motor
        left_frame = tk.Frame(motors_frame, bg='#2b2b2b')
        left_frame.pack(side='left', expand=True, fill='x', padx=10)
        
        tk.Label(left_frame, text="LEFT MOTOR", font=('Arial', 12, 'bold'),
                fg='#ff5555', bg='#2b2b2b').pack()
        
        self.left_canvas = tk.Canvas(left_frame, width=200, height=30,
                                     bg='#333333', highlightthickness=0)
        self.left_canvas.pack(pady=5)
        
        self.left_value = tk.Label(left_frame, text="0% | DIR: FWD",
                                   font=('Arial', 10), fg='white', bg='#2b2b2b')
        self.left_value.pack()
        
        # Right motor
        right_frame = tk.Frame(motors_frame, bg='#2b2b2b')
        right_frame.pack(side='right', expand=True, fill='x', padx=10)
        
        tk.Label(right_frame, text="RIGHT MOTOR", font=('Arial', 12, 'bold'),
                fg='#5555ff', bg='#2b2b2b').pack()
        
        self.right_canvas = tk.Canvas(right_frame, width=200, height=30,
                                      bg='#333333', highlightthickness=0)
        self.right_canvas.pack(pady=5)
        
        self.right_value = tk.Label(right_frame, text="0% | DIR: FWD",
                                    font=('Arial', 10), fg='white', bg='#2b2b2b')
        self.right_value.pack()
        
        # Control buttons frame
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(pady=20)

        # Button commands
        def cmd_forward():
            print("🔵 FORWARD button clicked")
            self.forward(60)

        def cmd_backward():
            print("🔴 BACKWARD button clicked")
            self.backward(60)

        def cmd_left():
            print("🟡 LEFT button clicked")
            self.turn_left(40)

        def cmd_right():
            print("🟡 RIGHT button clicked")
            self.turn_right(40)

        def cmd_stop():
            print("⏹️ STOP button clicked")
            self.stop()

        btn_forward = tk.Button(button_frame, text="FORWARD", bg='#00ff00', 
                               command=cmd_forward, width=8, height=2)
        btn_forward.pack(side='left', padx=5)

        btn_backward = tk.Button(button_frame, text="BACKWARD", bg='#ff5555', 
                                command=cmd_backward, width=8, height=2)
        btn_backward.pack(side='left', padx=5)

        btn_left = tk.Button(button_frame, text="LEFT", bg='#ffaa00', 
                            command=cmd_left, width=8, height=2)
        btn_left.pack(side='left', padx=5)

        btn_right = tk.Button(button_frame, text="RIGHT", bg='#ffaa00', 
                             command=cmd_right, width=8, height=2)
        btn_right.pack(side='left', padx=5)

        btn_stop = tk.Button(button_frame, text="STOP", bg='#ff0000', 
                            command=cmd_stop, width=8, height=2)
        btn_stop.pack(side='left', padx=5)

        # Bind keyboard keys
        self.root.bind('<Up>', lambda event: self.forward(60))
        self.root.bind('<Down>', lambda event: self.backward(60))
        self.root.bind('<Left>', lambda event: self.turn_left(40))
        self.root.bind('<Right>', lambda event: self.turn_right(40))
        self.root.bind('<space>', lambda event: self.stop())
        self.root.bind('<KP_Up>', lambda event: self.forward(60))
        self.root.bind('<KP_Down>', lambda event: self.backward(60))
        self.root.bind('<KP_Left>', lambda event: self.turn_left(40))
        self.root.bind('<KP_Right>', lambda event: self.turn_right(40))

        # Make sure the window can receive keyboard focus
        self.root.focus_set()

        print("✅ Buttons created successfully")
        print("⌨️ Keyboard controls enabled - Use arrow keys to drive!")
        print("   ↑ Forward | ↓ Backward | ← Left | → Right | Space = Stop")
        print(f"📊 Initial motor state - Left: {self.left_speed}, Right: {self.right_speed}")
        
        # Draw initial robot
        self._draw_robot()
        
        # Start update loop
        self._update_display()
        
        # Set close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start main loop
        self.root.mainloop()
    
    def _draw_robot(self):
        """Draw the robot on canvas with animation"""
        self.canvas.delete("all")
        
        # Draw floor/ground line
        self.canvas.create_line(0, 220, 600, 220, fill='#444444', width=2)
        
        # Robot body
        self.canvas.create_rectangle(200, 100, 400, 200,
                                    fill='#444444', outline='#00ff00',
                                    width=3)
        
        # Add texture
        self.canvas.create_line(220, 120, 380, 120, fill='#666666', width=1)
        self.canvas.create_line(220, 180, 380, 180, fill='#666666', width=1)
        
        # Camera
        self.canvas.create_oval(290, 60, 310, 80,
                              fill='#000000', outline='#00ff00',
                              width=2)
        
        # Camera lens (changes color based on mode)
        if self._get_mode() == "FORWARD":
            lens_color = '#88ff88'
        elif self._get_mode() == "BACKWARD":
            lens_color = '#ff8888'
        elif self._get_mode() == "TURNING":
            lens_color = '#ffff88'
        else:
            lens_color = '#88aaff'
            
        self.canvas.create_oval(295, 65, 305, 75,
                              fill=lens_color, outline='')
        
        # Wheels
        wheel_positions = [(150, 120), (150, 180), (450, 120), (450, 180)]
        
        for i, (x, y) in enumerate(wheel_positions):
            # Wheel circle
            self.canvas.create_oval(x-20, y-20, x+20, y+20,
                                   fill='#333333', outline='white', width=2)
            
            # Determine if this is left or right wheel
            is_left = x < 300
            speed = self.left_speed if is_left else self.right_speed
            direction = self.left_dir if is_left else self.right_dir
            
            if speed > 0:
                # Draw spinning effect
                angle = time.time() * speed * direction
                x1 = x + 15 * math.cos(angle)
                y1 = y + 15 * math.sin(angle)
                x2 = x - 15 * math.cos(angle)
                y2 = y - 15 * math.sin(angle)
                self.canvas.create_line(x1, y1, x2, y2,
                                       fill='white', width=2)
                
                # Draw direction arrow
                arrow_x = x + (25 if direction > 0 else -25)
                self.canvas.create_line(x, y, arrow_x, y, 
                                       fill='yellow', width=2, 
                                       arrow='last' if direction > 0 else 'first')
        
        # Draw path line based on direction
        if self._get_mode() == "FORWARD":
            self.canvas.create_line(300, 80, 300, 40, 
                                   fill='#00ff00', width=3, arrow='last')
            self.canvas.create_text(300, 20, text="FORWARD", 
                                   fill='#00ff00', font=('Arial', 12, 'bold'))
        elif self._get_mode() == "BACKWARD":
            self.canvas.create_line(300, 220, 300, 260, 
                                   fill='#ff5555', width=3, arrow='last')
            self.canvas.create_text(300, 280, text="BACKWARD", 
                                   fill='#ff5555', font=('Arial', 12, 'bold'))
        elif self._get_mode() == "TURNING":
            if self.left_dir > 0 and self.right_dir < 0:  # Turning right
                self.canvas.create_arc(400, 100, 500, 200, 
                                      start=0, extent=90,
                                      outline='#ffaa00', width=3, style='arc')
                self.canvas.create_text(480, 120, text="RIGHT", 
                                       fill='#ffaa00', font=('Arial', 12, 'bold'))
            else:  # Turning left
                self.canvas.create_arc(100, 100, 200, 200, 
                                      start=90, extent=90,
                                      outline='#ffaa00', width=3, style='arc')
                self.canvas.create_text(120, 120, text="LEFT", 
                                       fill='#ffaa00', font=('Arial', 12, 'bold'))
    
    def _update_display(self):
        """Update the display with current motor states"""
        if not self.root:
            return
            
        # Update mode
        mode = self._get_mode()
        self.mode_label.config(text=f"MODE: {mode}")
        
        # Update left motor
        self.left_canvas.delete("all")
        bar_width = int((self.left_speed / 100) * 200)
        color = '#ff5555' if self.left_dir > 0 else '#ff8888'
        self.left_canvas.create_rectangle(0, 0, bar_width, 30,
                                         fill=color, outline='')
        dir_text = "FWD" if self.left_dir > 0 else "REV"
        self.left_value.config(text=f"{self.left_speed}% | DIR: {dir_text}")
        
        # Update right motor
        self.right_canvas.delete("all")
        bar_width = int((self.right_speed / 100) * 200)
        color = '#5555ff' if self.right_dir > 0 else '#8888ff'
        self.right_canvas.create_rectangle(0, 0, bar_width, 30,
                                          fill=color, outline='')
        dir_text = "FWD" if self.right_dir > 0 else "REV"
        self.right_value.config(text=f"{self.right_speed}% | DIR: {dir_text}")
        
        # Redraw robot with updated state
        self._draw_robot()
        
        # Schedule next update
        if self.root:
            self.root.after(50, self._update_display)
    
    def _get_mode(self):
        """Determine current movement mode"""
        if self.left_speed == 0 and self.right_speed == 0:
            return "STOPPED"
        elif self.left_dir == self.right_dir:
            return "FORWARD" if self.left_dir > 0 else "BACKWARD"
        else:
            return "TURNING"
    
    # Motor control methods
    def forward(self, speed=60):
        print(f"🔵 Moving FORWARD at {speed}% (changing motor state)")
        self.left_speed = speed
        self.right_speed = speed
        self.left_dir = 1
        self.right_dir = 1
        
    def backward(self, speed=60):
        print(f"🔴 Moving BACKWARD at {speed}% (changing motor state)")
        self.left_speed = speed
        self.right_speed = speed
        self.left_dir = -1
        self.right_dir = -1
        
    def turn_left(self, speed=40):
        print(f"🟡 Turning LEFT at {speed}% (changing motor state)")
        self.left_speed = speed
        self.right_speed = speed
        self.left_dir = -1
        self.right_dir = 1
        
    def turn_right(self, speed=40):
        print(f"🟡 Turning RIGHT at {speed}% (changing motor state)")
        self.left_speed = speed
        self.right_speed = speed
        self.left_dir = 1
        self.right_dir = -1
        
    def stop(self):
        print(f"⏹️ STOPPED (changing motor state)")
        self.left_speed = 0
        self.right_speed = 0
        
    def get_state(self):
        return {
            'left_speed': self.left_speed,
            'right_speed': self.right_speed,
            'left_dir': self.left_dir,
            'right_dir': self.right_dir
        }
    
    def _on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()