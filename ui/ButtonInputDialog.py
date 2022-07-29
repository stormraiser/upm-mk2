import math

from PySide6 import QtCore, QtWidgets

class ButtonInputDialog(QtWidgets.QDialog):

	def __init__(self, parent, title, labels, ret_ptr):
		super().__init__(parent)
		self.ret_ptr = ret_ptr
		ret_ptr[0] = 0
		self.button_group = QtWidgets.QButtonGroup(self)
		self.setWindowTitle(title)
		if len(labels) <= 3:
			grid_w = len(labels)
			grid_h = 1
		else:
			grid_w = math.ceil((len(labels) + 0.5) ** 0.5)
			grid_h = (len(labels) - 1) // grid_w + 1
		layout = QtWidgets.QGridLayout()
		layout.setHorizontalSpacing(5)
		layout.setVerticalSpacing(5)
		for i in range(len(labels)):
			button = QtWidgets.QPushButton(labels[i])
			r = i // grid_w
			c = i % grid_w
			layout.addWidget(button, r, c)
			self.button_group.addButton(button, i)
		self.setLayout(layout)
		self.button_group.idClicked.connect(self.button_clicked)

	@QtCore.Slot()
	def button_clicked(self, button_id):
		self.ret_ptr[0] = button_id
		self.close()
