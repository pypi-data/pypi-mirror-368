# Superturtle

Superturtle provides extensions to Python's `turtle` module, supporting richer drawing, 
image export, and animation.

## Installation

First, make sure ImageMagick is installed. (If you use homebrew, this can be accomplished 
with `brew install imagemagick`.) Then, Superturtle can be installed using pip or poetry.

    pip install superturtle

## Usage

Please see [the Superturtle documentation](https://superturtle.readthedocs.io/en/latest/).

## Pedagogy

This module was originally developed as part of **Making With Code**, a constructionist
introductory computer science curriculum. Perhaps the most unusual design decision is this 
module's heavy use of context managers. For example:

    from turtle import forward
    from superturtle.stroke import dots

    with dots():
        forward(100)

![Drawing with dots context manager](documentation/doc_examples/context_manager.png)

Context managers are generally not introduced 
early in a CS curriculum, but they fit naturally with other constructs which contextualize
code blocks: loops, conditionals, and function definition. We hypothesize that introducing
intuitive context managers with easy-to-visualize effects may reinforce the more abstract
role of control structures, and may support students in learning to read indented Python code.
