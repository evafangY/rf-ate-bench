from .test_result import TestResult

def run_noise_blanked(ate):
    lines = []
    ok = True
    lines.append("Starting noise blanked test.")
    values = {}
    if hasattr(ate, "noise_unblanked_measure"):
        ate.noise_unblanked_measure()
        if hasattr(ate, "test_id_13204"):
            lines.append(f"Noise unblanked (13204): {round(ate.test_id_13204, 2)} dBm/Hz")
            values = {
                "13204_noise_unblanked_dbm_hz": getattr(ate, "test_id_13204", ""),
            }
    else:
        lines.append("Noise blanked function not available in AN8103_lib.")
        ok = False
    lines.append("Noise blanked test completed.")
    return lines, ok, values
