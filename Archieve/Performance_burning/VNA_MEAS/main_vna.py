import sys
from PyQt5.QtWidgets import QApplication
from Performance_burning.VNA_MEAS.ui_vna.main_window_vna import MainWindow

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
