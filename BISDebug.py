from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import time
start_time = time.perf_counter()

# class SingletonMeta(type(QObject)):
#     """Can be used instead of singleton decorator via metaclass=SingletonMeta"""
#     _instances = {}
#     def __call__(self, *args, **kwargs):
#         if self not in self._instances:
#             self._instances[self] = super().__call__(*args, **kwargs)
#         return self._instances[self]

def singleton(cls):
    """singleton decorator
    if instance of class exists, returns already existing instance
    interior wrapper function needed to see *args and **kwargs
    singleton decorator
    if instance of class exists, returns already existing instance
    interior wrapper function needed to see *args and **kwargs
    """
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

def get_debug_mananger():
    return DebugManager()

@singleton
class DebugManager(QObject):
    update_variable = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.debug_window = None

    def enable_debug(self):
        self.debug_window = DebugWindow()
        self.update_variable.connect(self.debug_window.update_variable)
        self.debug_window.show()

    def disable_debug(self):
        self.update_variable.disconnect(self.debug_window.update_variable)
        self.debug_window.close()
        self.debug_window = None

    def toggle_debug(self):
        if self.debug_window is not None:
            self.disable_debug()
        else: self.enable_debug()

class DebugMixin:
    _debug_manager = DebugManager()
    def __setattr__(self, name, value):
        self._debug_manager.update_variable.emit({
            'name': name,
            'class': self.__class__.__name__,
            'instance_id': id(self),
            'type': type(value).__name__,
            'value': value,
            'timestamp': round(time.perf_counter()-start_time, 2)
            })
        super().__setattr__(name, value)

class DebugItem(QStandardItem):
    def __init__(self, value):
        super().__init__(value)
        self.base_color = QColor(255, 255, 255, 255)#self.background().color()
        self.highlight_color = QColor(255, 190, 125, 255)
        self.fade_timer = QTimer()
        self.steps = 20
        self.fade_timer.timeout.connect(self.update_color)

    def start_fade(self):
        self.step = 0
        self.update_color()
        self.fade_timer.start(50)

    def update_color(self):
        """
        fades color from highlight -> base linearly
        """
        if self.step > self.steps:
            self.fade_timer.stop()
            return
        br, bg, bb, _ = self.base_color.getRgb()
        hr, hg, hb, _ = self.highlight_color.getRgb()
        r = hr + (br-hr)*self.step/self.steps
        g = hg + (bg-hg)*self.step/self.steps
        b = hb + (bb-hb)*self.step/self.steps
        self.setBackground(QColor(int(r), int(g), int(b), 255))
        self.step += 1

    def setData(self, value, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if value != self.text():
                self.start_fade()
        return super().setData(value, role)

@singleton
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

        def item_gen(v):
            item = DebugItem(str(v))
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled |
                Qt.ItemFlag.ItemIsSelectable
            )
            item.setFont(QFont('Lobster'))
            return item


        if self.horizontalHeaderItem(0) == None:
            self.setHorizontalHeaderLabels(list(var_info.keys()))
        if var_name in self.model_items:
            for k, v in var_info.items(): 
                self.model_items[var_name][k].setText(str(v))
        else:
            self.model_items[var_name] = {k: item_gen(v) for k, v in var_info.items()}
            self.appendRow(list(self.model_items[var_name].values()))

class VariableTab(QWidget):
    def __init__(self):
        super().__init__()
        self.model = DebugItemModel()
        tree_view = QTreeView()
        tree_view.setUniformRowHeights(True)
        tree_view.setAlternatingRowColors(True)
        tree_view.setSortingEnabled(True)
        tree_view.setRootIsDecorated(False)

        tree_view.setModel(self.model)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tree_view)

@singleton
class DebugWindow(QDialog):
    _model = DebugItemModel()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Window")
        self.setGeometry(100, 100, 900, 600)
        tab_widget = QTabWidget(self)
        self.variable_tab = VariableTab()

        tab_widget.addTab(self.variable_tab, 'Variables')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(tab_widget)

    def update_variable(self, var_info):
        self._model.update_variable(var_info)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() ==  Qt.Key.Key_F10 or event.key() == Qt.Key.Key_Escape:
            get_debug_mananger().toggle_debug()