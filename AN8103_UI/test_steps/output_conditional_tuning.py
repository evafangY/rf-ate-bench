from .test_result import TestResult
from ..specs import OUTPUT_COND_SPECS

def run_step2_oscilloscope_tests(ate, interaction_callback=None):
    """
    Step 2: Output Conditional Tuning (Oscilloscope Tests)
    Use 8-channel oscilloscope to measure 6 parameters simultaneously.
    """
    
    # IDs for oscilloscope tests
    osc_test_ids = ["14001", "14002", "14003", "14004", "14005", "14011"]
    
    # Measurement loop
    while True:
        # 1. Get measurements (simulated or real)
        measurements = {}
        if hasattr(ate, "get_oscilloscope_8ch_reading"):
            try:
                # Expecting ATE driver to return a dict with test IDs as keys
                measurements = ate.get_oscilloscope_8ch_reading()
            except Exception as e:
                print(f"Error reading oscilloscope: {e}")
        else:
            # Simulation data
            measurements = {
                "14001": 32.5,
                "14002": -50.1,
                "14003": -50.2,
                "14004": -40.1,
                "14005": -40.2,
                "14011": 36.5,
            }

        # 2. Check specs
        results = []
        all_passed = True
        report_lines = []

        for tid in osc_test_ids:
            if tid not in OUTPUT_COND_SPECS:
                continue
                
            label, unit, min_val, max_val = OUTPUT_COND_SPECS[tid]
            val = measurements.get(tid, -999.0)
            
            passed = True
            if min_val is not None and val < min_val: passed = False
            if max_val is not None and val > max_val: passed = False
            
            status = "PASS" if passed else "FAIL"
            if not passed: all_passed = False
            
            # Create TestResult object
            results.append(TestResult(
                test_id=tid,
                label=label,
                value=val,
                unit=unit,
                min_spec=min_val,
                max_spec=max_val,
                status="OK" if passed else "FAIL"
            ))
            
            # Create report line
            min_str = f"{min_val}" if min_val is not None else "-inf"
            max_str = f"{max_val}" if max_val is not None else "+inf"
            report_lines.append(f"{label}: {val:.2f} {unit} (Spec: {min_str} to {max_str}) -> {status}")

        # 3. If all passed, break
        if all_passed:
            break
            
        # 4. If failed, show results and allow retry
        msg = "Résultats des mesures (Oscilloscope 8 voies):\n\n" + "\n".join(report_lines)
        msg += "\n\nVeuillez ajuster les réglages si nécessaire.\nCliquez sur 'Mesurer' pour relancer la mesure."
        
        if interaction_callback:
            # Returns True for retry (Mesurer), False for continue/ignore (Continuer)
            should_retry = interaction_callback(msg)
            if not should_retry:
                break
        else:
            break

    return results, all_passed

def run_step2_resistance_head(ate, interaction_callback=None):
    label, unit, min_val, max_val = OUTPUT_COND_SPECS["14009"]
    return _run_manual_resistance(ate, interaction_callback, "14009", label, min_val, max_val)

def run_step2_resistance_body(ate, interaction_callback=None):
    label, unit, min_val, max_val = OUTPUT_COND_SPECS["14010"]
    return _run_manual_resistance(ate, interaction_callback, "14010", label, min_val, max_val)

def _run_manual_resistance(ate, interaction_callback, test_id, label, min_val, max_val):
    val = 0.0
    passed = False
    
    if interaction_callback:
        # Use new 'manual_input' type to request user input
        resp = interaction_callback({
            "type": "manual_input",
            "title": label,
            "instruction": f"Veuillez mesurer la résistance pour {label}.\nPlage acceptée: {min_val} - {max_val} Ohm.",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 100.0,
            "decimals": 2
        })
        
        if isinstance(resp, dict) and resp.get("ok"):
            val = resp.get("value", 0.0)
            if min_val <= val <= max_val:
                passed = True
    
    return [TestResult(
        test_id=test_id,
        label=label,
        value=val,
        unit="Ohm",
        min_spec=min_val,
        max_spec=max_val,
        status="OK" if passed else "FAIL"
    )], passed