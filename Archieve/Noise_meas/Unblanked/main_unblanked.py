from PyQt5.QtWidgets import QApplication
import sys
from Noise_meas.Unblanked.core_unblanked.workflow_unblanked import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
