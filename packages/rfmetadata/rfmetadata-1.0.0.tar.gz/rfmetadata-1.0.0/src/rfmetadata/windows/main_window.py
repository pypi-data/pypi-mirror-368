from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from rfmetadata.widgets.search_layout import SearchGroupBox
from rfmetadata.widgets.data_graph_layout import DataGraph3D
from PySide6.QtGui import QAction, QActionGroup
from rfmetadata.signal_manager.data_signal_manager import graph_type_manager, table_type_manager

from rfmetadata.widgets.query_result_layout import TableResultsWidget

class MainWindow(QMainWindow):
   def __init__(self):
        super().__init__()

        self.result_window= "in_window"
        
        self.setup_ui()
        
   def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.search = SearchGroupBox("Select minimum and maximum values")
        self.search.setMaximumHeight(200)
        layout.addWidget(self.search)
        
        self.graph = DataGraph3D()
        self.graph.setMinimumWidth(410)
        self.graph.setMinimumHeight(300)
        
        self.table = TableResultsWidget()
        self.table.setMinimumWidth(500)

        result_widget = QWidget()
        result_widget_layout = QHBoxLayout(result_widget)

        if self.result_window == "in_window":
           result_widget_layout.addWidget(self.table)
        
        result_widget_layout.addWidget(self.graph)

        layout.addWidget(result_widget)


        self.setWindowTitle("RF Sink Viewer")
        self.resize(800, 600)
        
        self.create_menu()
        

   def create_menu(self):
       global menubar
       menubar = self.menuBar()
   
       file_menu = menubar.addMenu("File")
   
       exit_action = QAction("Exit", self)
       exit_action.triggered.connect(self.close)
       file_menu.addAction(exit_action)
   
       help_menu = menubar.addMenu("Help")
   
       about_action = QAction("About", self)
       about_action.triggered.connect(self._show_about)
       help_menu.addAction(about_action)


       # parrent menu
       tool_menu = menubar.addMenu("Tools")
       select_graph_menu = tool_menu.addMenu("Graph")

       graph_group = QActionGroup(self)
       graph_group.setExclusive(True)

       graph_option_a = QAction("3D Scatter Plot", self, checkable=True)
       graph_option_a.setChecked(True)
       graph_option_a.triggered.connect(self.set_scatter)
       
       graph_option_b = QAction("3D Mesh Grid", self, checkable=True)
       graph_option_b.triggered.connect(self.set_meshgrid)

       graph_option_c = QAction("2D Line", self, checkable=True)
       graph_option_c.triggered.connect(self.set_line)

       graph_group.addAction(graph_option_a)
       graph_group.addAction(graph_option_b)
       graph_group.addAction(graph_option_c)

       select_graph_menu.addAction(graph_option_a)
       select_graph_menu.addAction(graph_option_b)
       select_graph_menu.addAction(graph_option_c)
       
       select_table_menu = tool_menu.addMenu("Table view")

       table_group = QActionGroup(self)       
       table_group.setExclusive(True)

       table_option_a = QAction("In Window", self, checkable=True)
       table_option_a.setChecked(True)
       table_option_a.triggered.connect(self.set_in_window)
       
       table_option_b = QAction("New Window", self, checkable=True)
       table_option_b.triggered.connect(self.set_new_window)

       table_group.addAction(table_option_a)
       table_group.addAction(table_option_b)

       select_table_menu.addAction(table_option_a)
       select_table_menu.addAction(table_option_b)


   def _show_about(self):
      QtWidgets.QMessageBox.about(self, "About", "RF Sink Viewer using PySide6\nTips:\n1-")

   def set_scatter(self):
      graph_type_manager.data_signal.emit("scatter")
      
   def set_meshgrid(self):
      graph_type_manager.data_signal.emit("meshgrid")

   def set_line(self):
      graph_type_manager.data_signal.emit("line")

   def set_in_window(self):
      self.result_window = "in_window"
      table_type_manager.data_signal.emit(False)
      menubar.clear()
      self.setup_ui()
      
   def set_new_window(self):
      self.result_window = "new_window"
      table_type_manager.data_signal.emit(True)
      menubar.clear()
      self.setup_ui()
