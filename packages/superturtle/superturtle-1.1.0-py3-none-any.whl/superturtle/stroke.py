# lines.py
# by Chris Proctor
# Helper functions for playing with how the turtle draws

# =============================================================================
# ! Advanced !
# =============================================================================
# This module contains some fancy code that we don't expect you to understand 
# yet. That's ok--as long as we know how to use code, we don't have to 
# understand everything about it. (Do you understand everything about 
# MacOS?) Check out the README for documentation on how to use this code. 

# Of course, if you want to dig into this module, feel free. You can ask a 
# teacher about it if you're interested. 
# =============================================================================

from itertools import cycle
from turtle import Turtle, pendown, penup, pencolor

class Segmenter:
    """
    Breaks a distance (length) into segments, which are yielded one at a time.
    Whatever's left over at the end gets yielded too. If start_at is given, 
    the pattern is offset by this much. For example:
    
        >>> from drawing.lines import Segmenter
        >>> list(Segmenter([1, 5]).segment(20))
        [1, 5, 1, 5, 1, 5, 1, 1]
    """

    def __init__(self, pattern):
        "Should be initialized with a pattern like [(10, penup), (20, pendown)]"
        self.pattern = pattern
        self.remainder = 0
        self.remainder_state = None
        self.pattern_cycle = cycle(pattern)

    def segment(self, length):
        """
        Segments `length` into chunks according to the pattern, yielding each chunk
        along with a boolean indicating whether there is more coming
        """
        if self.remainder > 0:
            if length > self.remainder:
                yield self.remainder, self.remainder_state
                length -= self.remainder
                self.remainder = 0
            else:
                yield length, self.remainder_state
                self.remainder -= length
                length = 0
        if length > 0: 
            for (seg, state) in self.pattern_cycle:
                if length >= seg:
                    yield seg, state
                    length -= seg
                else:
                    if length > 0:
                        yield length, state
                    self.remainder = seg - length
                    self.remainder_state = state
                    return 

def go_segmented(turtle, distance):
    "This is the fake go function that we're going to inject into the turtle"
    for seg, state in turtle.segmenter.segment(distance):
        state()
        turtle.true_go(seg)

def color_setter_factory(color):
    "Returns a function that sets the pencolor"
    def set_color():
        pencolor(color)
    return set_color

class dashes:
    """
    A context manager which causes a code block to draw with dashes. 

    Arguments:
        spacing (int): (Optional) The length of each dash and space in pixels. Defaults to 20.

    ::

        from superturtle.stroke import dashes
        with dashes():
            for side in range(4):
                forward(100)
                right(90)
    """
    def __init__(self, spacing=20):
        self.spacing = spacing
    
    def __enter__(self):
        Turtle.segmenter = Segmenter([(self.spacing, pendown), (self.spacing, penup)])
        Turtle.true_go = Turtle._go
        Turtle._go = go_segmented

    def __exit__(self, exc_type, exc_value, traceback):
        Turtle._go = Turtle.true_go
        del Turtle.true_go

class dots:
    """A context manager which causes a code block to draw with dots.

    Arguments:
        spacing (int): (Optional) The space between each dot in pixels. Defaults to 10.

    ::

        from turtle import forward, right
        from superturtle.stroke import dots
        with dots():
            for side in range(5):
                forward(100)
                right(360/5)
    """
    def __init__(self, spacing=10):
        self.spacing = spacing
    
    def __enter__(self):
        Turtle.segmenter = Segmenter([(1, pendown), (self.spacing, penup)])
        Turtle.true_go = Turtle._go
        Turtle._go = go_segmented

    def __exit__(self, exc_type, exc_value, traceback):
        Turtle._go = Turtle.true_go
        del Turtle.true_go

class rainbow:
    """A context manager which causes a code block to draw in rainbow colors.

    Arguments:
        spacing (int): (Optional) The length of each color segment. Defaults to 10.
        colors (list): (Optional) A sequence of color names (any valid inputs to 
            turtle.setcolor). By default, uses a rainbow.

    ::

        from turtle import forward
        from superturtle.stroke import rainbow
        with rainbow(colors=["black", "grey", "white"]):
            forward(60)
    """

    default_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    
    def __init__(self, spacing=10, colors=None):
        self.spacing = spacing
        self.colors = colors or rainbow.default_colors

    def __enter__(self):
        Turtle.segmenter = Segmenter([(self.spacing, color_setter_factory(color)) for color in self.colors])
        Turtle.true_go = Turtle._go
        Turtle._go = go_segmented

    def __exit__(self, exc_type, exc_value, traceback):
        Turtle._go = Turtle.true_go
        del Turtle.true_go
