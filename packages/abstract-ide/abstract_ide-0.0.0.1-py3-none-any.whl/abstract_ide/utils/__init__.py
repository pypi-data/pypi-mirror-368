#!/usr/bin/env python3
from .managers import *

def startGui():
    try:
        app = QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())
    except Exception:
        print(traceback.format_exc())


