import datetime


class PhaseResult:
    def __init__(self, phase_name, lines, ok, values=None):
        self.phase_name = phase_name
        self.lines = list(lines)
        self.ok = bool(ok)
        self.values = values or {}
        self.timestamp = datetime.datetime.now()


class SessionData:
    def __init__(self):
        self.technician_info = {}
        self.dut_info = {}
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.phase_results = []
        self.log_messages = []

    def add_phase_result(self, result):
        self.phase_results.append(result)

    def to_csv_rows(self):
        rows = []
        for result in self.phase_results:
            if result.values:
                for key, value in result.values.items():
                    rows.append(
                        {
                            "phase": result.phase_name,
                            "test_key": key,
                            "value": value,
                            "ok": result.ok,
                            "timestamp": result.timestamp.isoformat(),
                        }
                    )
            else:
                rows.append(
                    {
                        "phase": result.phase_name,
                        "test_key": "",
                        "value": "",
                        "ok": result.ok,
                        "timestamp": result.timestamp.isoformat(),
                    }
                )
        return rows


PHASE_IMAGE_MAP = {
    "Diagnostic": "Models/Pics/Master_Slave_Connection.png",
    "Output conditional tuning": "Output_cond/Pics/Amplifier.png",
    "Power module gain tuning": "SW_Tunning/Pics/Amplifier.png",
    "Input conditional board tuning": "Input_cond/Pics/Amplifier.png",
    "Performance test / burn": "Performance_burning/assets/Pics/Mesure.png",
    "Noise blanked": "Noise_meas/Pics/Noise.jpg",
}

