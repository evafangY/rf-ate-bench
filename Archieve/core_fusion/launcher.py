# -----------------------------
# IMPORTS DES bibliothèques
# -----------------------------

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# -----------------------------
# IMPORTS DES WORKFLOWS
# -----------------------------

# DIAGNOSTICS
from Diag.core.workflow import MainWindow as DiagWindow
from Diag.core.visa_setup import connect_instruments as connect_diag


# INPUT CONDITIONER
from Input_cond.core.workflow import MainWindow as InputWindow
from Input_cond.core.visa_setup import connect_instruments as connect_input


# OUTPUT CONDITIONER
from Output_cond.core.workflow import MainWindow as OutputWindow
from Output_cond.core.visa_setup import connect_instruments as connect_output


# NOISE MEASUREMENT
# -------------------------------------- Unblanked ---------------------------------------------
from Noise_meas.Unblanked.core_unblanked.workflow_unblanked import MainWindow as NoiseUnblankedWindow
from Noise_meas.Unblanked.core_unblanked.visa_setup_unblanked import connect_instruments as connect_noise_blanked

# -------------------------------------- Blanked -----------------------------------------------
from Noise_meas.Blanked.core_blanked.workflow_blanked import MainWindow as NoiseBlankedWindow
from Noise_meas.Blanked.core_blanked.visa_setup_blanked import connect_instruments as connect_noise_unblanked


# PERFORMANCE / BURNING
# -------------------------------------- Scope config ---------------------------------------------
from Performance_burning.SCOPE_MEAS.ui_scope.main_window_scope import MainWindowScope as PerfScopeWindow
from Performance_burning.SCOPE_MEAS.core_scope.visa_setup_scope import Connect_instruments_scope as connect_perf_scope

# -------------------------------------- Vna config ---------------------------------------------
from Performance_burning.VNA_MEAS.ui_vna.main_window_vna import MainWindowVna as PerfVnaWindow
from Performance_burning.VNA_MEAS.core_vna.visa_setup_vna import Connect_instruments_vna as connect_perf_vna

# SOFTWARE TUNNING
from SW_Tunning.core.workflow import MainWindow as TuningWindow
from SW_Tunning.core.visa_setup import connect_instruments as connect_tuning


# ============================================================
#   SOUS‑MENU NOISE
# ============================================================
class NoiseSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noise Measurement – Choix du mode")
        self.resize(400, 200)

        layout = QVBoxLayout()

        title = QLabel("Choisissez le mode Noise")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        btn_blank = QPushButton("Blanked")
        btn_blank.clicked.connect(self.launch_blanked)
        layout.addWidget(btn_blank)

        btn_unblank = QPushButton("Unblanked")
        btn_unblank.clicked.connect(self.launch_unblanked)
        layout.addWidget(btn_unblank)

        self.setLayout(layout)

    def launch_blanked(self):
        scope, swg, psu, srfd_com, com_status = connect_noise_blanked()
        self.window = NoiseBlankedWindow(scope, swg, psu, srfd_com)
        self.window.show()

    def launch_unblanked(self):
        scope, swg, psu, srfd_com, com_status = connect_noise_unblanked()
        self.window = NoiseUnblankedWindow(scope, swg, psu, srfd_com)
        self.window.show()



# ============================================================
#   SOUS‑MENU PERFORMANCE
# ============================================================
class PerformanceSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Performance / Burning – Choix du mode")
        self.resize(400, 200)

        layout = QVBoxLayout()

        title = QLabel("Choisissez le mode Performance")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        btn_scope = QPushButton("Scope")
        btn_scope.clicked.connect(self.launch_scope)
        layout.addWidget(btn_scope)

        btn_vna = QPushButton("VNA")
        btn_vna.clicked.connect(self.launch_vna)
        layout.addWidget(btn_vna)

        self.setLayout(layout)

    def launch_scope(self):
        scope, swg, psu, srfd_com, com_status = connect_perf_scope()
        self.window = PerfScopeWindow(scope, swg, psu, srfd_com, com_status)
        self.window.show()

    def launch_vna(self):
        scope, swg, psu, srfd_com, com_status = connect_perf_vna()
        self.window = PerfVnaWindow(scope, swg, psu, srfd_com, com_status)
        self.window.show()


# ============================================================
#   LAUNCHER PRINCIPAL
# ============================================================
class Launcher(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GE Healthcare – Test Launcher")
        self.resize(500, 450)

        # --- BACKGROUND BLANC ---
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()

        # --- TITRE ---
        title = QLabel("Choisissez un test")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color: #4B0082; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- STYLE DES BOUTONS ---
        button_style = """
            QPushButton {
                background-color: #4B0082;
                color: white;
                padding: 12px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5C0AA0;
            }
            QPushButton:pressed {
                background-color: #3A0066;
            }
        """

        # --- BOUTONS ---
        layout.addWidget(self._btn("Diagnostics", self.launch_diag, button_style))
        layout.addWidget(self._btn("Input Conditioner", self.launch_input, button_style))
        layout.addWidget(self._btn("Output Conditioner", self.launch_output, button_style))
        layout.addWidget(self._btn("Noise Measurement", self.launch_noise, button_style))
        layout.addWidget(self._btn("Performance / Burning", self.launch_perf, button_style))
        layout.addWidget(self._btn("Software Tunning", self.launch_tuning, button_style))

        layout.addStretch()
        self.setLayout(layout)

    def _btn(self, text, callback, style):
        b = QPushButton(text)
        b.setStyleSheet(style)
        b.clicked.connect(callback)
        return b


    # -----------------------------
    # FONCTIONS DE LANCEMENT
    # -----------------------------
    def launch_diag(self):
        srfd_com, srfd_amp_master, srfd_amp_slave, com_status = connect_diag()
        self.window = DiagWindow()
        self.window.show()

    def launch_input(self):
        scope, swg33522B, swg33611A, srfd_com = connect_input()
        self.window = InputWindow(scope, swg33522B, swg33611A, srfd_com)
        self.window.show()

    def launch_output(self):
        rm, scope, swg33611A, com_status = connect_output()
        self.window = OutputWindow(rm, scope, swg33611A, com_status)
        self.window.show()

    def launch_noise(self):
        self.window = NoiseSelector()
        self.window.show()

    def launch_perf(self):
        self.window = PerformanceSelector()
        self.window.show()

    def launch_tuning(self):
        scope, srfd_com, srfd_amp_master, srfd_amp_slave, com_status = connect_tuning()
        self.window = TuningWindow(scope, srfd_com, srfd_amp_master, srfd_amp_slave, com_status)
        self.window.show()