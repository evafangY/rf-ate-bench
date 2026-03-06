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
        self.current_rf_input_dbm = 0.0
        self.current_mode = "body"

        class _SimComm:
            def __init__(self, parent):
                self.parent = parent
                self.state = 1
            def standby(self):
                self.state = 1
            def body(self):
                self.parent.current_mode = "body"
                self.state = 3
            def head(self):
                self.parent.current_mode = "head"
                self.state = 2

        class _SimRF:
            def __init__(self, parent):
                self.parent = parent
            def config(self, dbm, _mode):
                self.parent.current_rf_input_dbm = float(dbm)
            def operate(self):
                return None

        self.comm = _SimComm(self)
        self.rf = _SimRF(self)
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
                "temp1": 25.0,
                "temp2": 28.0,
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
                "temp1": 25.5,
                "temp2": 28.5,
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
        
    def noise_blanked_measure(self):
        """Simulate noise blanked measurement."""
        # Spec 13202: Coherent noise (narrow spectrum) < -143.00 dBm/Hz
        # Spec 13203: Random noise (broad spectrum) < -160.00 dBm/Hz
        import time
        import random
        
        # Simulate measurement delay
        time.sleep(1.0)
        
        # Generate passing values with some variation
        # Coherent noise: Target -150 +/- 2
        self.test_id_13202 = -150.0 + random.uniform(-2.0, 2.0)
        
        # Random noise: Target -165 +/- 2
        self.test_id_13203 = -165.0 + random.uniform(-2.0, 2.0)
        
        print(f"[SIM] Noise Blanked Measure:")
        print(f"  - 13202 (Coherent): {self.test_id_13202:.2f} dBm/Hz")
        print(f"  - 13203 (Random):   {self.test_id_13203:.2f} dBm/Hz")


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

    def gain_tuning_power_measure(self, body_head):
        mode = body_head or self.current_mode
        if mode == "head":
            target = 60.0 if self.current_rf_input_dbm <= 0.1 else 63.5
        else:
            target = 68.5 if self.current_rf_input_dbm <= 0.1 else 72.0
        return target + random.uniform(-0.12, 0.12)

    def poweroff(self):
        self.comm.state = 0

    def noise_unblanked_measure(self):
        self.test_id_13204 = -150.0 + random.uniform(-5.0, 5.0)

    def single_pulse_measure(self):
        self.test_id_13301 = -40.0 + random.uniform(-0.5, 0.5)

    def harmonic_output_measure(self):
        self.test_id_13201 = -35.0 + random.uniform(-2.0, 2.0)

    def interpulse_stability_measure(self):
        self.test_id_13302 = -50.0 + random.uniform(-1.0, 1.0)
        self.test_id_13303 = -40.0 + random.uniform(-1.0, 1.0)

    def gain_flatness_measure(self):
        self.test_id_13101 = 50.0 + random.uniform(-5.0, 5.0)
        self.test_id_13106 = 60.0 + random.uniform(-0.5, 0.5)

    def fidelity_measure(self):
        self.test_id_13205 = 0.40 + random.uniform(-0.1, 0.1)

    def stress(self, sequence_id):
        val = 1.0 + random.uniform(-0.1, 0.1)
        if sequence_id == 1: self.test_id_13108 = val
        elif sequence_id == 2: self.test_id_13109 = val
        elif sequence_id == 3: self.test_id_13110 = val
        elif sequence_id == 4: self.test_id_13111 = val
        elif sequence_id == 5: self.test_id_13112 = val

    def stress_burst(self, sequence_id):
        val = 1.0 + random.uniform(-0.1, 0.1)
        if sequence_id == 6: self.test_id_13113 = val
        elif sequence_id == 7: self.test_id_13114 = val
        elif sequence_id == 8: self.test_id_13115 = val


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
