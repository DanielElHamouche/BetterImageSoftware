from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Window")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.variable_labels = {}

    def update_variable(self, name, value):
        """Update the displayed variable in the debug window."""
        if name in self.variable_labels:
            self.variable_labels[name].setText(f"{name}: {value}")
        else:
            label = QLabel(f"{name}: {value}")
            self.variable_labels[name] = label
            self.layout.addWidget(label)