import sys, pathlib

from PySide6 import QtWidgets

import ui

if __name__ == "__main__":
	base_path = pathlib.Path(__file__).resolve()
	sys.path.append(str(base_path.parent / 'lib'))

	app = QtWidgets.QApplication([])

	main_window = ui.MainWindow(base_path)
	main_window.resize(800, 600)
	main_window.show()

	if len(sys.argv) > 1:
		start_puzzle_path = pathlib.Path(sys.argv[1]).resolve()
		main_window.load_puzzle(start_puzzle_path)

	sys.exit(app.exec())
