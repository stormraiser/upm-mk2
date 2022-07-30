

from PySide6 import QtCore, QtWidgets, QtGui

class PuzzleInspector(QtWidgets.QWidget):

	def __init__(self, parent = None, f = QtCore.Qt.WindowFlags()):
		super().__init__(parent, f)

		self.puzzle = None
		self.item_model = QtGui.QStandardItemModel(0, 2, self)
		#self.item_model.setHorizontalHeaderLabels(['Position', 'Block'])
		self.tree_view = QtWidgets.QTreeView(self)
		self.tree_view.setModel(self.item_model)
		header = QtWidgets.QHeaderView(QtCore.Qt.Horizontal)
		self.tree_view.setHeader(header)

		self.root_item = None

		layout = QtWidgets.QHBoxLayout()
		layout.addWidget(self.tree_view)
		self.setLayout(layout)

	@QtCore.Slot()
	def update_state(self):
		self.update_item(self.root_item)

	def update_item(self, item):
		for i in range(item.rowCount()):
			pos_id = item.child(i, 0).data()
			if pos_id >= 0:
				block_id = self.puzzle.state[pos_id]
				if block_id >= 0:
					item.child(i, 1).setData(self.puzzle.block_list[block_id].name, QtCore.Qt.DisplayRole)
					item.child(i, 0).setData(QtGui.QBrush(QtGui.Qt.black), QtGui.Qt.ForegroundRole)
					item.child(i, 1).setData(QtGui.QBrush(QtGui.Qt.black), QtGui.Qt.ForegroundRole)
				else:
					item.child(i, 1).setData('None', QtCore.Qt.DisplayRole)
					item.child(i, 0).setData(QtGui.QBrush(QtGui.Qt.lightGray), QtGui.Qt.ForegroundRole)
					item.child(i, 1).setData(QtGui.QBrush(QtGui.Qt.lightGray), QtGui.Qt.ForegroundRole)
			else:
				self.update_item(item.child(i, 0))

	def set_puzzle(self, puzzle):
		self.puzzle = puzzle

		self.item_model.clear()
		self.item_list = [None] * len(self.puzzle.pos_list)

		#'''
		self.root_item = QtGui.QStandardItem('All positions')
		class_rows = []
		for pos_class in self.puzzle.pos_tree.children:
			group_rows = []
			for group in pos_class.children:
				orbit_rows = []
				for orbit in group.children:
					ring_rows = []
					for ring in orbit.children:
						pos_rows = []
						for pos in ring.children:
							pos_name_item = QtGui.QStandardItem(self.puzzle.pos_list[pos])
							pos_name_item.setData(pos)
							block_id = self.puzzle.start_state[pos]
							if block_id >= 0:
								block_name_item = QtGui.QStandardItem(self.puzzle.block_list[block_id].name)
								pos_name_item.setData(QtGui.QBrush(QtGui.Qt.black), QtGui.Qt.ForegroundRole)
								block_name_item.setData(QtGui.QBrush(QtGui.Qt.black), QtGui.Qt.ForegroundRole)
							else:
								block_name_item = QtGui.QStandardItem('None')
								pos_name_item.setData(QtGui.QBrush(QtGui.Qt.lightGray), QtGui.Qt.ForegroundRole)
								block_name_item.setData(QtGui.QBrush(QtGui.Qt.lightGray), QtGui.Qt.ForegroundRole)
							pos_rows.append([pos_name_item, block_name_item])

						if len(pos_rows) == 1:
							ring_rows.append(pos_rows[0])
						else:
							ring_item = QtGui.QStandardItem('Ring ' + ring.name)
							ring_item.setData(-1)
							for pos_row in pos_rows:
								ring_item.appendRow(pos_row)
							ring_rows.append([ring_item, QtGui.QStandardItem('')])

					if len(ring_rows) == 1:
						orbit_rows.append(ring_rows[0])
					else:
						orbit_item = QtGui.QStandardItem('Orbit ' + orbit.name)
						orbit_item.setData(-1)
						for ring_row in ring_rows:
							orbit_item.appendRow(ring_row)
						orbit_rows.append([orbit_item, QtGui.QStandardItem('')])

				if len(orbit_rows) == 1:
					group_rows.append(orbit_rows[0])
				else:
					group_item = QtGui.QStandardItem('Group ' + group.name)
					group_item.setData(-1)
					for orbit_row in orbit_rows:
						group_item.appendRow(orbit_row)
					group_rows.append([group_item, QtGui.QStandardItem('')])

			if len(group_rows) == 1:
				class_rows.append(group_rows[0])
			else:
				class_item = QtGui.QStandardItem('Class ' + pos_class.name)
				class_item.setData(-1)
				for group_row in group_rows:
					class_item.appendRow(group_row)
				class_rows.append([class_item, QtGui.QStandardItem('')])

		for class_row in class_rows:
			self.root_item.appendRow(class_row)

		self.item_model.appendRow([self.root_item, QtGui.QStandardItem('')])
		self.item_model.setHeaderData(0, QtCore.Qt.Horizontal, 'Position')
		self.item_model.setHeaderData(1, QtCore.Qt.Horizontal, 'Current Block')
		self.tree_view.expandAll()
		self.tree_view.setColumnWidth(0, 200)
		self.tree_view.setColumnWidth(1, 150)
		#'''
