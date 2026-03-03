from .test_result import TestResult

def run_output_conditional_simulation(ate=None):
    lines = []
    ok = True
    lines.append("Starting output conditional tuning.")
    
    body_power = 0.0
    head_power = 0.0
    
    if ate and hasattr(ate, "output_tuning"):
        try:
            body_power, head_power = ate.output_tuning()
        except Exception:
            ok = False
            lines.append("Error during output tuning.")
    else:
        # If no ATE function available, just log warning
        lines.append("ATE output_tuning function not available.")
        ok = False

    lines.append(f"Measured body output: {body_power:.2f} dBm")
    lines.append(f"Measured head output: {head_power:.2f} dBm")
    lines.append("Output conditional tuning completed.")
    
    values = {
        "body_output_power_dbm": body_power,
        "head_output_power_dbm": head_power,
    }
    return lines, ok, values
