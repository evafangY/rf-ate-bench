import datetime
from .phase_services import TestResult

class PhaseResult:
    def __init__(self, phase_name, lines, ok, values=None, test_results=None):
        self.phase_name = phase_name
        self.lines = list(lines)
        self.ok = bool(ok)
        self.values = values or {}
        # New: Store structured TestResult objects
        self.test_results = test_results or []
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
            # Prefer TestResult objects if available
            if result.test_results:
                for tr in result.test_results:
                    if tr.test_id and tr.test_id not in ("INFO", "ERROR"):
                        rows.append({
                            "phase": result.phase_name,
                            "test_key": tr.test_id,
                            "value": tr.value,
                            "ok": tr.status == "PASS" or tr.status == "OK",
                            "timestamp": result.timestamp.isoformat(),
                            # Extra fields for detailed report
                            "label": tr.label,
                            "unit": tr.unit,
                            "min_spec": tr.min_spec,
                            "max_spec": tr.max_spec,
                            "status": tr.status
                        })
            # Fallback to legacy 'values' dict
            elif result.values:
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
            # Fallback to generic phase result
            else:
                 # Skip generic phase results for CSV if they don't have data
                 pass
        return rows
    
    def to_full_report_data(self):
        """Returns a dictionary suitable for JSON/HTML report generation"""
        report = {
            "technician": self.technician_info,
            "dut": self.dut_info,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "phases": []
        }
        
        for p in self.phase_results:
            phase_data = {
                "name": p.phase_name,
                "timestamp": p.timestamp.isoformat(),
                "ok": p.ok,
                "lines": p.lines,
                "results": []
            }
            if p.test_results:
                 for tr in p.test_results:
                     phase_data["results"].append({
                         "test_id": tr.test_id,
                         "label": tr.label,
                         "value": tr.value,
                         "unit": tr.unit,
                         "min": tr.min_spec,
                         "max": tr.max_spec,
                         "status": tr.status
                     })
            elif p.values:
                # Legacy support
                for k, v in p.values.items():
                    phase_data["results"].append({
                        "test_id": k,
                        "value": v
                    })
            
            report["phases"].append(phase_data)
            
        return report
