# The Universal Permuting Machine, Mark II

This is a programmable simulator for combination puzzles written in python.

This project is in a very early stage of development. I did not intend to publish it so hastily but some people asked for it so here it is. I'm still working on the core part that reads instructions from the puzzle definition file and builds the puzzle. The current UI is mostly for testing and will be properly rewritten once I finish the core part.

Run `test.py`. Currently there is only the standard Rubik's Cube to play with, but you can try to decipher the puzzle definition file (`cube_3.py`) and make your own puzzle. I'll write the documentation for the puzzle definition file later.

Requirements: NumPy, pyglet and ModernGL
