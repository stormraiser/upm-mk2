import sys, pathlib

from PySide6 import QtCore, QtGui, QtWidgets

import core
from .PuzzleDisplay import PuzzleDisplay

class MainWindow(QtWidgets.QWidget):

	def __init__(self, base_path):
		super().__init__()

		self.base_path = base_path
		self.control_penal = QtWidgets.QWidget()
		self.display = PuzzleDisplay()

		self.open_button = QtWidgets.QPushButton("Open...")
		self.reload_button = QtWidgets.QPushButton("Reload")
		self.reset_button = QtWidgets.QPushButton("Reset")
		self.scramble_button = QtWidgets.QPushButton("Scramble")
		self.play_button = QtWidgets.QPushButton("Play")
		self.inspect_button = QtWidgets.QPushButton("Inspect")
		self.color_button = QtWidgets.QPushButton("Color...")
		self.settings_button = QtWidgets.QPushButton("Settings...")
		self.info_box = QtWidgets.QTextEdit()

		control_layout = QtWidgets.QGridLayout()

		control_layout.addWidget(self.open_button, 0, 0)
		control_layout.addWidget(self.reload_button, 0, 1)
		control_layout.addWidget(self.reset_button, 1, 0)
		control_layout.addWidget(self.scramble_button, 1, 1)
		control_layout.addWidget(self.play_button, 2, 0)
		control_layout.addWidget(self.inspect_button, 2, 1)
		control_layout.addWidget(self.color_button, 3, 0)
		control_layout.addWidget(self.settings_button, 3, 1)
		control_layout.addWidget(self.info_box, 4, 0, 1, 2)

		control_layout.setHorizontalSpacing(5)
		control_layout.setVerticalSpacing(5)
		control_layout.setRowStretch(4, 1)

		self.control_penal.setLayout(control_layout)
		self.control_penal.setFixedWidth(200)

		main_layout = QtWidgets.QHBoxLayout()
		main_layout.addWidget(self.control_penal)
		main_layout.addWidget(self.display)
		self.setLayout(main_layout)

		self.open_button.clicked.connect(self.open_file)

	@QtCore.Slot()
	def open_file(self):
		puzzle_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open", str(self.base_path))[0]
		if len(puzzle_path) > 0:
			puzzle_path = pathlib.Path(puzzle_path).resolve()
			puzzle_dir = str(puzzle_path.parent)
			sys.path.append(puzzle_dir)
			puzzle = core.Puzzle(puzzle_path, self.base_path.parent / 'lib')
			self.display.set_puzzle(puzzle)
			sys.path.remove(puzzle_dir)
