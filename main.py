import sys, pathlib

from PySide6 import QtWidgets

import ui

if __name__ == "__main__":
	base_path = pathlib.Path(__file__).resolve()
	sys.path.append(str(base_path.parent / 'lib'))

	app = QtWidgets.QApplication([])

	main_window = ui.MainWindow(base_path)
	#main_window = ui.PuzzleDisplay()
	main_window.resize(800, 600)
	main_window.show()

	sys.exit(app.exec())
