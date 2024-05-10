from PyQt5.QtWidgets import QApplication
import sys
from py_includes.app import App

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    # ex.show()
    sys.exit(app.exec_())
