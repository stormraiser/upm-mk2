# The Universal Permuting Machine, Mark II

This is a programmable simulator for combination puzzles written in Python.

This project is in a very early stage of development. I did not intend to publish it so hastily but some people asked for it so here it is. I'm still working on the core part that reads instructions from the puzzle definition file and builds the puzzle. The current UI is mostly for testing and will be properly rewritten once I finish the core part.

Run `test.py <filename>`. `<filename>` is the path to a puzzle definition file. Those are themselves Python codes. Examples can be found in the `puzzle_collection` directory. The documentation will gradually be added to the project wiki. Controls: dragging with left mouse button and (for some puzzles, when there are highlighted pieces) clicking with left or right mouse button to make a move. Dragging with right mouse button to rotate the view.

Requirements: NumPy, trimesh, pyglet and ModernGL
