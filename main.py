import sys
from PyQt6.QtWidgets import QApplication
from BetterImageSoftware import MainWindow
from BISDebug import *
from CustomWidgets import *
DEBUGGING_ON_START = True


if __name__ == '__main__':
    app = QApplication([])
    if DEBUGGING_ON_START: 
        get_debug_mananger().toggle_debug()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())