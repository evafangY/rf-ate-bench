import datetime
from .phase_services import TestResult
from .specs import (
    PERFORMANCE_SPECS, 
    OUTPUT_COND_SPECS, 
    INPUT_COND_SPECS, 
    NOISE_SPECS, 
    DIAGNOSTIC_SPECS,
    DIAGNOSTIC_VOLTAGE_SPECS
)

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

    def get_exportable_test_results(self):
        """
        Retrieves, filters, and sorts test results for CSV export.
        
        Filtering: Only includes results with IDs present in specs.
        Sorting: Diagnostics (bias, alim, temp) -> Numeric IDs -> Others.
        """
        # 1. Build valid Test IDs set from specs
        valid_ids = set()
        for spec_dict in (PERFORMANCE_SPECS, OUTPUT_COND_SPECS, INPUT_COND_SPECS, NOISE_SPECS, DIAGNOSTIC_SPECS, DIAGNOSTIC_VOLTAGE_SPECS):
            valid_ids.update(spec_dict.keys())
        
        # 2. Gather filtered results
        all_results = []
        for result in self.phase_results:
            if result.test_results:
                for tr in result.test_results:
                    # Check against valid IDs
                    if str(tr.test_id) in valid_ids:
                        all_results.append(tr)
            elif result.values:
                 # Legacy support
                 for k, v in result.values.items():
                     if str(k) in valid_ids:
                         # Create a dummy TestResult
                         tr = TestResult(test_id=k, label=k, value=v, unit="", min_spec=None, max_spec=None, status="INFO")
                         all_results.append(tr)

        if not all_results:
             return []

        # 3. Sort results based on TestID
        # Order: Diagnostics first (bias, alim, temp), then Numeric IDs sorted numerically
        def get_sort_key(tr):
            tid = str(tr.test_id)
            # Diagnostics
            if tid.startswith("bias"):
                return (0, 0, tid)
            if tid.startswith("alim"):
                return (0, 1, tid)
            if tid.startswith("temp"):
                return (0, 2, tid)
            
            # Numeric IDs
            if tid.isdigit():
                return (1, int(tid), tid)
            
            # Fallback
            return (2, 0, tid)

        all_results.sort(key=get_sort_key)
        return all_results

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
