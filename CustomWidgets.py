from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import math

class ExponentialSlider(QSlider):
    """
    implemented based on https://www.desmos.com/calculator/xz7vkxtyfh
    Logic -->
    First half of slider should be linear from 0-100. (S set to 100)
    Second half of slider should be exponential from 100-200, with y1 (self.max_zoom) being the max zoom value.
    max zoom should be calculated based on the image size to be 1 pixel full screen.
    For now hardset to 500
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.setValue(100)
        self.setTickInterval(50)

        self.end = 200
        self.split = 100
        self.max_zoom = 500
        self.d = (self.end**2-2*self.end*self.split+self.split**2)/(self.max_zoom-self.end)
        self.setRange(1,self.end)

    def value(self):
        if (value := super().value()) <= 100: return super().value()
        return int(value + ((value-self.split)**2)/self.d) 
            
class CustomStatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: green; color: white;")
        self.setSizeGripEnabled(False)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.status_label = QLabel("Status: OK")
        self.addPermanentWidget(self.status_label, 1)
        
        self.lbl_zoom_level = QLabel("100%")
        self.lbl_zoom_level.setMinimumWidth(28)
        self.lbl_zoom_level.justifyContent = Qt.AlignmentFlag.AlignRight
        self.addPermanentWidget(self.lbl_zoom_level, 0)
        
        self.slider = ExponentialSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(lambda: self.lbl_zoom_level.setText(f"{self.slider.value()}%"))
        self.slider.setMaximumSize(150, 20)
        self.addPermanentWidget(self.slider, 1)

        
    def show_context_menu(self, pos): #Add functionality to enable / disbable status bar
        menu = QMenu()
        action1 = QAction("Option 1", self)
        action2 = QAction("Option 2", self)
        menu.addAction(action1)
        menu.addAction(action2)
        menu.exec(self.mapToGlobal(pos))


class TestWidget(QDialog):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tab_widget = QTabWidget(self)
        tab1 = TabOne()
        tab2 = TabTwo()
        tab_widget.addTab(tab1, 'Tab 1')
        tab_widget.addTab(tab2, 'Tab 2')

        layout.addWidget(tab_widget)

class TabTwo(QWidget):
    def __init__(self):
        super().__init__()
        tw = QTreeWidget()
        tw.setAlternatingRowColors(True)
        tw.setHeaderLabels(['HELLO', 'TEST'])
        item = QTreeWidgetItem(tw, ['1', '2'])
        QTreeWidgetItem(item, ['3', '4'])

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tw)

class TabOne(QWidget):
    def __init__(self):
        super().__init__()
        data_model = DebugItemModel()
        data_model.update_variable({
            'name': 'aga_name',
            'class': 'aga_class',
            'instance_id': 'aga_instance_id',
            'type': 'aga_type',
            'value': 'aga_value',
            'timestamp': 'aga_timestamp'
            })
        tree_view = QTreeView()
        tree_view.setModel(data_model)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tree_view)

class DebugItemModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.model_items = {}

    def update_variable(self, var_info: dict):
        """
        Updates or adds a variable's data to the ItemModel
        Maintains a dict model_items with {var_name: {attribute: QStandardIten(str(value)) for attribute, value in var_info.items()}}
        Parameters:
        var_info (dict):    A dictionary containing variable information.
                            Must include a 'name' key used as a unique identifier.
        """
        var_name = var_info['name']

        if self.horizontalHeaderItem(0) == None:
            self.setHorizontalHeaderLabels(list(var_info.keys()))
        if var_name in self.model_items:
            for k, v in var_info.items(): 
                self.model_items[var_name][k].setText(v)
        else:
            self.model_items[var_name] = {k: QStandardItem(str(v)) for k, v in var_info.items()}
            self.appendRow(list(self.model_items[var_name].values()))