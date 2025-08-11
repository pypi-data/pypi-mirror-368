from .appfileinventory import *

import sys
from PyQt6.QtWidgets import QApplication

def runapp(type="FileInventory"):
    if isinstance(type, str) and type == "FileInventory":
        app = QApplication(sys.argv)
        windows = FileInventoryApp()
        windows.show() 
        sys.exit(app.exec())