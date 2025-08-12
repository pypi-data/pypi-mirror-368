# animation.py
# ----------------------
# By Chris Proctor
#

from pathlib import Path
from shutil import rmtree
from subprocess import run
from superturtle.movement import no_delay
from turtle import (
    Turtle, 
    left, 
    right, 
    clear, 
    home, 
    heading, 
    setheading, 
    isdown,     
    hideturtle, 
    penup, 
    pendown, 
    forward,
    getcanvas,
)
from superturtle.easing import linear
from itertools import cycle
from time import time, sleep

FRAMES_PATH = Path(".frames")

def animate(frames=1, loop=False, debug=False, gif_filename=None):
    """Runs an animation, frame by frame, at a fixed frame rate of 20 fps.
    An animation consists of a bunch of frames shown one after another. 
    Before creating an animation, create a static image and then think about
    how you would like for it to move. The simplest way to use `animate` is
    with no arguments; this produces a static image. (Not much of an animation!)::

        for frame in animate():
            draw_my_picture(frame)

    Once you are happy with your static image, specify `frames` and `animate`
    will run the provided code block over and over, drawing one frame at a time::
    
        for frame in animate(frames=6, debug=True):
            draw_my_picture(frame)

    Because we set `debug` to `True`, you will see the following output in the Terminal.
    Additionally, since we are in debug mode, you need to press enter to advance one
    frame at a time.::

        Drawing frame 0
        Drawing frame 1
        Drawing frame 2
        Drawing frame 3
        Drawing frame 4
        Drawing frame 5

    Arguments:
        frames (int): The total number of frames in your animation. 
        loop (bool): When True, the animation will play in a loop.
        debug (bool): When True, renders the animation in debug mode.
        gif_filename (str): When provided, saves the animation as a gif, with 10 frames per second.
    """
    start_time = time()
    if frames <= 0:
        raise AnimationError("frames must be a positive integer")
    frame_delta = 0.05
    hideturtle()
    if debug:
        frame_iterator = debug_iter(frames)
    elif loop and not gif_filename:
        frame_iterator = cycle(range(frames))
    else:
        frame_iterator = range(frames)
    if gif_filename:
        if FRAMES_PATH.exists():
            if FRAMES_PATH.is_dir():
                rmtree(FRAMES_PATH)
            else:
                FRAMES_PATH.unlink()
        FRAMES_PATH.mkdir()
        
    for frame_number in frame_iterator:
        frame = Frame(frames, frame_number, debug=debug)
        if time() < start_time + frame_number * frame_delta:
            sleep(start_time + frame_number * frame_delta - time())
        with no_delay():
            home()
            clear()
            yield frame
        if gif_filename:
            filename = FRAMES_PATH / f"frame_{frame_number:03d}.eps"
            canvas = getcanvas()
            canvas.postscript(file=filename)
            canvas.delete("all")
            
    if gif_filename:
        loopflag = "-loop 0 " if loop else ""
        run(f"magick -delay 5 -dispose Background {loopflag}{FRAMES_PATH}/frame_*.eps {gif_filename}", shell=True, check=True)
        rmtree(FRAMES_PATH)

class Frame:
    """ Represents one frame in an animation.
    When creating an animation, `animate` will yield one `Frame` for each 
    frame. The `Frame` can be used to check information, such as the current 
    frame index (the first frame's index is 0; the tenth frame's index is 9). 
    The `Frame` can also be used to create motion through the use of transformations. 
    A transformation is a change to the picture which gradually changes from frame
    to frame. The three supported transformations are `rotate`, `scale`, and 
    `translate`. 

    The transformations provided by Superturtle animation frames (`rotate`, `translate`, `scale`)
    only work for relative turtle movement (e.g. `forward`, `back`, `left`, `right`). 
    Absolute turtle movement (e.g. `goto`, `setheading`) will not be affected by 
    transformations.

    """
    def __init__(self, num_frames, index=0, debug=False):
        self.debug = debug
        self.num_frames = num_frames
        self.index = index
        self.stack = []
        self.log("Drawing frame {}".format(self.index))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        exit = self.stack.pop()
        exit()

    def rotate(self, start, stop=None, first_frame=None, last_frame=None, cycles=1, mirror=False, easing=None):
        """Runs the code block within a rotation::

                for frame in animate(frames=30):
                    with frame.rotate(0, 90):
                        square(100)

            Arguments:
                start (int): the initial value.
                stop (int): (optional) the final value. If not provided, this will be a static 
                    rotation of `start` on every frame.
                first_frame (int): (optional) The first frame at which this rotation should be    
                    interpolated. If given, the rotation will be `start` at `first_frame` 
                    and all prior frames. If not given, interpolation starts at the beginning
                    of the animation.
                last_frame(int): (optional) The last frame at which this rotation should be 
                    interpolated. If given, the rotation will be `stop` at `last_frame`
                    and all later frames. If not given, interpolation ends at the end of the
                    animation.
                cycles (int): (optional) Number of times the animation should be run.
                mirror (bool): (optional) When True, the animation runs forward and then backwards 
                    between `first_frame` and `last_frame`.
                easing (function): (optional) An easing function to use.
        """
        value = self.interpolate(start, stop, first_frame, last_frame, cycles, mirror, easing)
        left(value)
        self.stack.append(lambda: right(value))
        self.log("Rotating by {}".format(value))
        return self

    def scale(self, start, stop=None, first_frame=None, last_frame=None, cycles=1, mirror=False, easing=None):
        """Scales the code block. For this to work correctly, make sure you start from the 
        center of the drawing in the code block::

                for frame in animate(frames=30):
                    with frame.scale(1, 2):
                        square(100)

        Arguments:
            start (int): the initial value.
            stop (int): (optional) the final value. If not provided, this will be a static 
            scaling of `start` on every frame.
            first_frame (int): (optional) The first frame at which this scaling should be    
                interpolated. If given, the scaling will be `start` at `first_frame` 
                and all prior frames. If not given, interpolation starts at the beginning
                of the animation.
            last_frame (int): (optional) The last frame at which this scaling should be 
                interpolated. If given, the scaling will be `stop` at `last_frame`
                and all later frames. If not given, interpolation ends at the end of the
                animation.
            cycles (int): (optional) Number of times the animation should be run.
            mirror (bool): (optional) When True, the animation runs forward and then backwards 
                between `first_frame` and `last_frame`.
            easing (function): (optional) An easing function to use.
        """
        value = self.interpolate(start, stop, first_frame, last_frame, cycles, mirror, easing)
        repair = self._scale_turtle_go(value)
        self.stack.append(repair)
        self.log("Scaling by {}".format(value))
        return self

    def translate(self, start, stop=None, first_frame=None, last_frame=None, cycles=1, mirror=False, easing=None):
        """Translates (moves) the code block in the current coordinate space::

                for frame in animate(frames=30):
                    with frame.translate([0, 0], [100, 100]):
                        square(100)

            Arguments:
                start (int): the initial value.
                stop (int): (optional) the final value. If not provided, this will be a static 
                    translation of `start` on every frame.
                first_frame (int): (optional) The first frame at which this translation should be    
                    interpolated. If given, the translation will be `start` at `first_frame` 
                    and all prior frames. If not given, interpolation starts at the beginning
                    of the animation.
                last_frame (int): (optional) The last frame at which this translation should be 
                    interpolated. If given, the translation will be `stop` at `last_frame`
                    and all later frames. If not given, interpolation ends at the end of the
                    animation.
                cycles (int): (optional) Number of times the animation should be run.
                mirror (bool): (optional) When True, the animation runs forward and then backwards 
                    between `first_frame` and `last_frame`.
                easing (function): (optional) An easing function to use.
        """
        if stop:
            x0, y0 = start
            x1, y1 = stop
            dx = self.interpolate(x0, x1, first_frame, last_frame, cycles, mirror, easing)
            dy = self.interpolate(y0, y1, first_frame, last_frame, cycles, mirror, easing)
        else:
            dx, dy = start

        def scoot(x, y):
            pd = isdown()
            penup()
            forward(x)
            left(90)
            forward(y)
            right(90)
            if pd:
                pendown()

        scoot(dx, dy)
        self.stack.append(lambda: scoot(-dx, -dy))
            
        self.log("Translating by ({}, {})".format(dx, dy))
        return self

    def _scale_turtle_go(self, scale_factor):
        """Patches `Turtle._go` with a version which scales all motion
        by `scale_factor`. Returns a repair function which will restore
        `Turtle._go` when called.
        """
        prior_go = Turtle._go
        def scaled_go(turtle_self, distance):
            prior_go(turtle_self, distance * scale_factor)
        Turtle._go = scaled_go
        def repair():
            Turtle._go = prior_go
        return repair

    def log(self, message):
        if self.debug:
            print("  " * len(self.stack) + message)

    def interpolate(self, start, stop=None, first_frame=None, last_frame=None, cycles=1, mirror=False, easing=None):
        """Interpolates a value between `start` and `stop`.
        Interpolation is the process of finding a value partway between two known values.
        In this function, the two known values are `start` and `stop`, and we need to find 
        an appropriate value partway between the two endpoints. When the frame is `first_frame`, 
        the value should be `start` and when the frame is `last_frame` the value should be `stop`.
        When the frame is halfway in between the first and last frames, the value should be halfway
        between the endpoints. 
        Interpolation is used internally by all three of the transformations (rotate, scale, and translate), 
        but you can use it directly if you want. For example, if you want to scale just one side of a 
        rectangle::

            def rectangle(a, b):    
                for _ in range(2):
                    forward(a)
                    right(90)
                    forward(b)
                    right(90)
            for frame in animate(frames=60):
                height = frame.interpolate(20, 80)
                width = 100 - height
                rectangle(height, width)
        
        Arguments:
            start (int): the initial value.
            stop (int): (optional) the final value. If not provided, `start` is returned.
            first_frame (int): (optional) The first frame at which interpolation should be    
                used. If given, the value will be `start` at `first_frame` 
                and all prior frames. If not given, interpolation starts at the beginning
                of the animation.
            last_frame (int): (optional) The last frame at which interpolation should be 
                used. If given, the value will be `stop` at `last_frame`
                and all later frames. If not given, interpolation ends at the end of the
                animation.
            cycles (int): (optional) Number of times the animation should be run.
            mirror (bool): (optional) When True, the interpolated value reaches `stop` halfway between
                `first_frame` and `last_frame`, then returns to `start`.
            easing (function): (optional) An easing function to use.
        """
        if stop is None:
            return start
        first_frame = first_frame or 0
        last_frame = last_frame or self.num_frames
        if first_frame >= last_frame:
            raise AnimationError("last_frame must be greater than first_frame")
        period = (last_frame - first_frame) / cycles
        ix = min(max(first_frame, self.index), last_frame)
        if ix >= last_frame:
            t = 1
        else:
            t = ((ix - first_frame) % period) / period
        if mirror: 
            t = 1 - abs(2*t - 1)
        if easing is None:
            easing = linear
        t = easing().ease(t)
        return start + t * (stop - start)

def debug_iter(max_val=None):
    "An iterator which yields only when input is "
    HELP = '?'
    INCREMENT = ['', 'f']    
    DECREMENT = ['b']
    value = 0
    print("In debug mode. Enter {} for help.".format(HELP))
    while True:
        yield value % max_val if max_val else value
        command = None
        while command not in INCREMENT and command not in DECREMENT:
            if command == HELP:
                print("Debug mode moves one frame at a time.")
                print("Enter 'f' or '' (blank) to move forward. Enter 'b' to move backward.")
            command = input()
        if command in INCREMENT:
            value += 1
        else:   
            value -= 1

class AnimationError(Exception):
    pass
