from PySide6.QtWidgets import QGroupBox, QGridLayout, QLabel, QPushButton, QDoubleSpinBox, QSpacerItem, QSizePolicy
from PySide6.QtCore import QLocale, Qt
from rfmetadata.windows.query_result_window import show_query_results
from rfmetadata.signal_manager.data_signal_manager import signal_manager
import requests

class SearchGroupBox(QGroupBox):
    
    def __init__(self, parent=None):

        self.min_power = 20.0
        self.max_power = 60.0
        self.min_frequency = 103.0
        self.max_frequency = 109.0

        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):

        layout = QGridLayout()
        self.setLayout(layout)
        
        self.min_power_spin = QDoubleSpinBox()
        self.min_power_spin.setRange(self.min_power,self.max_power)
        self.min_power_spin.setValue(20.0)
        self.min_power_spin.setSingleStep(0.01)
        self.min_power_spin.setDecimals(2) 
        self.min_power_spin.setLocale(QLocale(QLocale.English))


        self.max_power_spin = QDoubleSpinBox()
        self.max_power_spin.setRange(self.min_power,self.max_power)
        self.max_power_spin.setValue(self.max_power)
        self.max_power_spin.setSingleStep(0.01)
        self.max_power_spin.setDecimals(2) 
        self.max_power_spin.setLocale(QLocale(QLocale.English))

    
        self.min_frequency_spin = QDoubleSpinBox()
        self.min_frequency_spin.setRange(self.min_frequency,self.max_frequency)
        self.min_frequency_spin.setValue(self.min_frequency)
        self.min_frequency_spin.setSingleStep(0.01)
        self.min_frequency_spin.setDecimals(2) 
        self.min_frequency_spin.setLocale(QLocale(QLocale.English))


        self.max_frequency_spin = QDoubleSpinBox()
        self.max_frequency_spin.setRange(self.min_frequency,self.max_frequency)
        self.max_frequency_spin.setValue(self.max_frequency)
        self.max_frequency_spin.setSingleStep(0.01)
        self.max_frequency_spin.setDecimals(2) 
        self.max_frequency_spin.setLocale(QLocale(QLocale.English))


        self.power_label = QLabel("Power:")
        self.min_power_label = QLabel("Min:",alignment=(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter))
        self.max_power_label = QLabel("Max:",alignment=(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter))

        self.frequency_label = QLabel("Frequency:")
        self.min_frequency_label = QLabel("Min:",alignment=(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter))
        self.max_frequency_label = QLabel("Max:",alignment=(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter))

        self.error_message = QLabel("")
        self.error_message.setStyleSheet("QLabel { color : red}")

        self.button = QPushButton("Search")
        
        layout.addWidget(self.power_label,0,0)
        layout.addItem(QSpacerItem(200, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        layout.addWidget(self.min_power_label,0,1)
        layout.addWidget(self.min_power_spin,0,2)
        layout.addWidget(self.max_power_label,0,3)
        layout.addWidget(self.max_power_spin,0,4)        
        
        layout.addWidget(self.frequency_label,1,0)
        layout.addItem(QSpacerItem(200, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        layout.addWidget(self.min_frequency_label,1,1)
        layout.addWidget(self.min_frequency_spin,1,2)
        layout.addWidget(self.max_frequency_label,1,3)
        layout.addWidget(self.max_frequency_spin,1,4)


        layout.addWidget(self.error_message)
        layout.addWidget(self.button,2,0)


        self.button.clicked.connect(self.search_database)
        
    def search_database(self): 
        min_power = self.min_power_spin.value()
        max_power = self.max_power_spin.value()
        min_frequency = self.min_frequency_spin.value()
        max_frequency = self.max_frequency_spin.value()

        if min_frequency > max_frequency or min_power > max_power:
            self.error_message.setText("min values can't be larger than max values !")

        else:
            self.error_message.setText("")
            result = requests.get(f'http://127.0.0.1:5000/search/{min_power}/{max_power}/{min_frequency}/{max_frequency}')

            if result:
                signal_manager.data_signal.emit(result.json())
                show_query_results(result.json())
            else:
                self.error_message.setText("No results !")
        
       