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
        self.master.biasQ32 = 0
        

    def input_tuning(self, mode, dbm):
        target = 0
        if mode == "body":
            if dbm == -4: target = -4.5
            elif dbm == 10: target = -4.5
            elif dbm == 0: target = -4.5
        elif mode == "head":
            if dbm == -4: target = -13.5
            elif dbm == 10: target = -13.5
            elif dbm == 0: target = -13.5
            
        # Simulate values with some noise to allow "tuning" (randomness)
        # In a real scenario, the user would adjust something and this would read it.
        # Here we just return a value that might be in spec or not.
        # Let's return a value that is mostly in spec to allow passing.
        val = target + random.uniform(-0.2, 0.2)
        return val, val

    def performance_test(self):
        # Pulse stability
        self.test_id_13301 = 0.15  # Single pulse drop (dB)
        self.test_id_13302 = 0.05  # Gain inter pulse stability (dB)
        self.test_id_13303 = 0.50  # Phase inter pulse stability (deg)
        
        # Input/Output
        self.test_id_12007 = 1.20  # Input VSWR
        self.test_id_13101 = 0.20  # Body Bandwidth (dB)
        self.test_id_13102 = 0.20  # Head Bandwidth (dB)
        self.test_id_13103 = 72.50 # Body output power nominal (dBm)
        self.test_id_13104 = 63.50 # Head output power nominal (dBm)
        self.test_id_13105 = 1.00  # Body output margin (dB)
        self.test_id_13106 = 72.00 # Body gain (dB)
        self.test_id_13107 = 63.00 # Head delta gain (dB)
        
        # Stress sequence variations (%)
        self.test_id_13108 = 1.0
        self.test_id_13109 = 1.0
        self.test_id_13110 = 1.0
        self.test_id_13111 = 1.0
        self.test_id_13112 = 1.0
        self.test_id_13113 = 1.0
        self.test_id_13114 = 1.0
        self.test_id_13115 = 1.0
        
        # Harmonic & Noise
        self.test_id_13201 = -35.0  # Harmonic output (dBc)
        self.test_id_13204 = -75.0  # Unblanked output noise (dBm/Hz)
        
        # Fidelity (Gain/Phase Non-linearity & Differential)
        self.test_id_13205 = 0.40   # Gain NL Body Fwd
        self.test_id_13206 = 0.05   # Diff Gain Body Fwd
        self.test_id_13207 = -0.05  # Diff Gain Body Fwd
        self.test_id_13208 = -0.10  # Diff Gain Body Fwd
        self.test_id_13209 = 3.00   # Phase NL Body Fwd
        self.test_id_13210 = 0.20   # Diff Phase Body Fwd
        self.test_id_13211 = -0.50  # Diff Phase Body Fwd
        self.test_id_13212 = -1.00  # Diff Phase Body Fwd
        
        self.test_id_13213 = 0.40   # Gain NL Body Rev
        self.test_id_13214 = 0.05   # Diff Gain Body Rev
        self.test_id_13215 = -0.05  # Diff Gain Body Rev
        self.test_id_13216 = -0.10  # Diff Gain Body Rev
        self.test_id_13217 = 3.00   # Phase NL Body Rev
        self.test_id_13218 = 0.20   # Diff Phase Body Rev
        self.test_id_13219 = -0.50  # Diff Phase Body Rev
        self.test_id_13220 = -1.00  # Diff Phase Body Rev 

    def output_tuning(self):
        body_power = 72.5 + random.uniform(-0.5, 0.5)
        head_power = 63.5 + random.uniform(-0.5, 0.5)
        return body_power, head_power

    def gain_tuning(self):
        master_gain = 69.0 + random.uniform(-0.3, 0.3)
        slave_gain = 69.0 + random.uniform(-0.3, 0.3)
        self.master.Gai = master_gain
        self.slave.Gai = slave_gain

    def poweroff(self):
        self.comm.state = 0

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
