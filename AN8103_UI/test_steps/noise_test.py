from .test_result import TestResult

def run_noise_blanked(ate):
    lines = []
    ok = True
    lines.append("Starting noise blanked test.")
    values = {}
    if hasattr(ate, "noise_blanked_measure"):
        ate.noise_blanked_measure()
        
        # Check for coherent noise blanked (13202)
        if hasattr(ate, "test_id_13202"):
            val_13202 = getattr(ate, "test_id_13202", "N/A")
            lines.append(f"Coherent noise blanked (13202): {round(val_13202, 2) if isinstance(val_13202, (int, float)) else val_13202} dBm/Hz")
            values["13202_noise_blanked_coherent"] = val_13202
            
        # Check for random noise blanked (13203)
        if hasattr(ate, "test_id_13203"):
            val_13203 = getattr(ate, "test_id_13203", "N/A")
            lines.append(f"Random noise blanked (13203): {round(val_13203, 2) if isinstance(val_13203, (int, float)) else val_13203} dBm/Hz")
            values["13203_noise_blanked_random"] = val_13203
            
    else:
        lines.append("Noise blanked function not available in AN8103_lib.")
        ok = False
    lines.append("Noise blanked test completed.")
    return lines, ok, values
