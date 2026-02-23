import sys
from PyQt5.QtWidgets import QApplication
from Performance_burning.SCOPE_MEAS.ui_scope.main_window_scope import MainWindowScope

def main():
    app = QApplication(sys.argv)
    w = MainWindowScope()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
