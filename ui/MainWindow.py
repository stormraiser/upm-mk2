import sys, pathlib

from PySide6 import QtCore, QtGui, QtWidgets

import core
from .PuzzleDisplay import PuzzleDisplay
from .ButtonInputDialog import ButtonInputDialog
from .PuzzleInspector import PuzzleInspector

class MainWindow(QtWidgets.QWidget):

	def __init__(self, base_path):
		super().__init__()

		self.base_path = base_path
		self.control_penal = QtWidgets.QWidget()
		self.display = PuzzleDisplay()
		self.inspector = PuzzleInspector()

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
		main_layout.addWidget(self.inspector)
		self.inspector.hide()
		self.setLayout(main_layout)

		self.open_button.clicked.connect(self.open)
		self.reload_button.clicked.connect(self.reload)
		self.play_button.clicked.connect(self.show_display)
		self.inspect_button.clicked.connect(self.show_inspector)

		self.display.puzzle_state_changed.connect(self.inspector.update_state)

		self.last_puzzle_path = None

	def load_puzzle(self, puzzle_path):
		if puzzle_path is not None:
			self.last_puzzle_path = puzzle_path
			puzzle_dir = str(puzzle_path.parent)
			sys.path.append(puzzle_dir)
			puzzle = core.Puzzle(self, puzzle_path, self.base_path.parent / 'lib')
			sys.path.remove(puzzle_dir)
			self.display.set_puzzle(puzzle)
			self.inspector.set_puzzle(puzzle)

	@QtCore.Slot()
	def open(self):
		puzzle_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open", str(self.base_path))[0]
		puzzle_path = pathlib.Path(puzzle_path).resolve() if puzzle_path != '' else None
		self.load_puzzle(puzzle_path)

	@QtCore.Slot()
	def reload(self):
		self.load_puzzle(last_puzzle_path)

	@QtCore.Slot()
	def show_display(self):
		self.display.show()
		self.inspector.hide()

	@QtCore.Slot()
	def show_inspector(self):
		self.display.hide()
		self.inspector.show()

	def get_input_buttons(self, title, labels):
		ret_ptr = [0]
		dialog = ButtonInputDialog(self, title, labels, ret_ptr)
		dialog.exec()
		return ret_ptr[0]

	def keyPressEvent(self, event):
		if event.key() in [QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt]:
			self.display.keyPressEvent(event)
		else:
			super().keyPressEvent(event)

	def keyReleaseEvent(self, event):
		if event.key() in [QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt]:
			self.display.keyReleaseEvent(event)
		else:
			super().keyReleaseEvent(event)
