#from Diag.core.workflow import MainWindow as DiagnosticsWindow
#from Diag.core.visa_setup import connect_instruments as connect_diag

from PyQt5.QtWidgets import QApplication
from core_fusion.launcher import Launcher
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Launcher()
    w.show()
    sys.exit(app.exec_())
