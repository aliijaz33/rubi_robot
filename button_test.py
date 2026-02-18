#!/usr/bin/env python3
"""
Minimal tkinter button test
"""

import tkinter as tk

def test_forward():
    print("🔵 FORWARD button clicked - WORKING!")

def test_backward():
    print("🔴 BACKWARD button clicked - WORKING!")

def test_left():
    print("🟡 LEFT button clicked - WORKING!")

def test_right():
    print("🟡 RIGHT button clicked - WORKING!")

def test_stop():
    print("⏹️ STOP button clicked - WORKING!")

# Create window
root = tk.Tk()
root.title("Button Test")
root.geometry("400x200")

# Create buttons
btn_frame = tk.Frame(root)
btn_frame.pack(expand=True)

btn1 = tk.Button(btn_frame, text="FORWARD", bg='#00ff00', command=test_forward, width=10, height=2)
btn1.pack(side='left', padx=5)

btn2 = tk.Button(btn_frame, text="BACKWARD", bg='#ff5555', command=test_backward, width=10, height=2)
btn2.pack(side='left', padx=5)

btn3 = tk.Button(btn_frame, text="LEFT", bg='#ffaa00', command=test_left, width=10, height=2)
btn3.pack(side='left', padx=5)

btn4 = tk.Button(btn_frame, text="RIGHT", bg='#ffaa00', command=test_right, width=10, height=2)
btn4.pack(side='left', padx=5)

btn5 = tk.Button(btn_frame, text="STOP", bg='#ff0000', command=test_stop, width=10, height=2)
btn5.pack(side='left', padx=5)

print("Button test window opened - click buttons to test")

root.mainloop()