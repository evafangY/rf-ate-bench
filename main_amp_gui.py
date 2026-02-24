import os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ATE_Lib_AN8103.ate_lib import ate_init, COMM_Error, ATE_Instrument_Error
from AN8103_UI.main_window import MainWindow
import random


class FakeATE:
    def __init__(self):
        self.test_id_13301 = -0.3
        self.test_id_13201 = 35.0
        self.test_id_13204 = -152.0
        self.is_simulation = True
        self.comm = type("Comm", (), {"state": 1})()
        self.master = type(
            "Side",
            (),
            {
                "alim_140": 140.0,
                "alim_48": 48.0,
                "alim_p15": 15.0,
                "alim_m15": -15.0,
                "fault": 0,
                "error": 0,
                "Gai": 69.0,
                "biasQ20": 500,
            },
        )()
        self.slave = type(
            "Side",
            (),
            {
                "alim_140": 140.0,
                "alim_48": 48.0,
                "alim_p15": 15.0,
                "alim_m15": -15.0,
                "fault": 0,
                "error": 0,
                "Gai": 69.0,
            },
        )()

    def diagnostics(self):
        self.comm.state = 1
        bias_names = (
            [f"biasQ{i}" for i in range(3, 11)]
            + [f"biasQ{i}" for i in range(11, 19)]
            + [f"biasQ{i}" for i in range(19, 27)]
            + ["biasQ27", "biasQ28", "biasQ31", "biasQ32", "biasQ33", "biasQ34", "biasQ35"]
        )
        for side in (self.master, self.slave):
            side.alim_140 = 140.0
            side.alim_48 = 48.0
            side.alim_p15 = 15.0
            side.alim_m15 = -15.0
            side.fault = 0
            side.error = 0
            side.Gai = 69.0
            for name in bias_names:
                setattr(side, name, 200)
        # Simulate master error: decimal 64 (0x40)
        self.master.fault = 0
        self.master.error = 64
        self.master.biasQ32 = 200
        

    def performance_test(self):
        self.test_id_13301 = -0.2 + random.uniform(-0.05, 0.05)
        self.test_id_13201 = 34.0 + random.uniform(-2.0, 2.0)
        self.test_id_13204 = -150.0 + random.uniform(-5.0, 5.0)
        self.test_id_13101 = 0.3 + random.uniform(-0.1, 0.1)
        self.test_id_13102 = 0.3 + random.uniform(-0.1, 0.1)
        self.test_id_13106 = 60.0 + random.uniform(-1.0, 1.0)
        self.test_id_13107 = 60.0 + random.uniform(-1.0, 1.0)
        self.test_id_13108 = 2.0 + random.uniform(-0.5, 0.5)
        self.test_id_13109 = 2.0 + random.uniform(-0.5, 0.5)
        self.test_id_13110 = 2.0 + random.uniform(-0.5, 0.5)
        self.test_id_13111 = 2.0 + random.uniform(-0.5, 0.5)
        self.test_id_13112 = 2.0 + random.uniform(-0.5, 0.5)
        self.test_id_13301 = -40.0 + random.uniform(-0.5, 0.5)

    def noise_unblanked_measure(self):
        self.test_id_13204 = -150.0 + random.uniform(-5.0, 5.0)

    def single_pulse_measure(self):
        self.test_id_13301 = -40.0 + random.uniform(-0.5, 0.5)

    def harmonic_output_measure(self):
        self.test_id_13201 = -35.0 + random.uniform(-2.0, 2.0)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 11))
    simulation = "--sim" in sys.argv
    ate = None
    if not simulation:
        try:
            ate = ate_init()
        except COMM_Error as e:
            QMessageBox.warning(None, "Amplifier error", f"Error {hex(e.code)}\nStarting in simulation mode.")
            simulation = True
        except ATE_Instrument_Error as e:
            QMessageBox.warning(None, "Instrument error", f"{e.instrument}\nStarting in simulation mode.")
            simulation = True
        except Exception as e:
            QMessageBox.warning(None, "Initialization error", f"{e}\nStarting in simulation mode.")
            simulation = True
    if simulation:
        ate = FakeATE()
    window = MainWindow(ate)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
