from turtle import *
from animation import animate

def square(size):
    for i in range(4):
        fd(size)
        rt(90)

def rect(a, b):
    for _ in range(2):
        forward(a)
        right(90)
        forward(b)
        right(90)

def fly(x):
    penup()
    forward(x)
    pendown()

def rotation_demo(frame):
    with frame.rotate(0, 90, mirror=True):
        square(200)
        with frame.rotate(0, 90, mirror=True):
            square(100)
            with frame.rotate(0, 90, mirror=True):
                square(50)
                with frame.rotate(0, 90, mirror=True):
                    square(25)

def scale_demo(frame):
    with frame.scale(0, 200, mirror=True):
        square(1)

def translation_demo(frame):
    with frame.translate((0,0), (100, 0), first_frame=0, last_frame=15):
        with frame.translate((0, 0), (0, 100), first_frame=15, last_frame=30):
            with frame.translate((0,0), (-100, 0), first_frame=30, last_frame=45):
                with frame.translate((0, 0), (0, -100), first_frame=45, last_frame=60):
                    square(50)

def composition_demo(frame):
    with frame.rotate(0, 90, first_frame=15):
        arm_length = frame.interpolate(50, 150, mirror=True)
        rect(arm_length, 20)
        fly(arm_length)
        with frame.scale(50, 100, first_frame=15):
            square(1)

for frame in animate(frames=60, loop=True, gif_filename="composition.gif"):
    #rotation_demo(frame)
    #scale_demo(frame)
    #translation_demo(frame)
    composition_demo(frame)

input("Press enter...")
