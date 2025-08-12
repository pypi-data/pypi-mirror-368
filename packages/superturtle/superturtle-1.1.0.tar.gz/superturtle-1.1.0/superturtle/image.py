# image.py
# ----------------------
# By Chris Proctor
#

from turtle import getcanvas, Turtle
from pathlib import Path
from subprocess import run
from svg_turtle import SvgTurtle

def save(filename):
    """Saves the canvas as an image.

    Arguments:
        filename (str): Location to save the file, including file extension.
    """
    temp_file = Path("_temp.eps")
    getcanvas().postscript(file=temp_file)
    cmd = f"magick {temp_file} -colorspace RGB {filename}"
    run(cmd, shell=True, check=True)
    temp_file.unlink()

class save_svg:
    """A context manager which saves turtle drawing in SVG format.

    Arguments:
        width (int): Width of resulting SVG file.
        height (int): Height of resulting SVG file.
        filename (str): Location to save resulting SVG.

    ::

        from superturtle.image import save_svg
        with save_svg(500, 500, "image.svg"):
            circle(100)
    """
    def __init__(self, width, height, filename):
        self.svg_turtle = SvgTurtle(width, height)
        self.filename = filename
    def __enter__(self):
        Turtle._pen = self.svg_turtle
    def __exit__(self, type, value, traceback):
        self.svg_turtle.save_as(self.filename)
        Turtle._pen = None

