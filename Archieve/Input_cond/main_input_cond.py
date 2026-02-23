from PyQt5.QtWidgets import QApplication
import sys
from Input_cond.core.workflow import MainWindow

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
