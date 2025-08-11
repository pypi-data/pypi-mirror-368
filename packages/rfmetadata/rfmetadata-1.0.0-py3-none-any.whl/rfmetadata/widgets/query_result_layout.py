from PySide6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt
from rfmetadata.signal_manager.data_signal_manager import signal_manager

class TableResultsWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        
        self.result = ""
        signal_manager.data_signal.connect(self.set_result)
            # Configure table
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)

        self.setColumnCount(4)
        self.setRowCount(20)
        self.setHorizontalHeaderLabels(["ID", "frequency", "power", "datetime"])

    def set_result(self, data):
       self.result = data
       self.setup_ui(self.result)

    def setup_ui(self, query):
        self.setRowCount(len(query))
        for row, row_data in enumerate(query):
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, col, item)



        
        


