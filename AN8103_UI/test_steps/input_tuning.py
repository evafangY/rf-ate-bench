import math
from ..test_utils import create_test_result
from .test_result import TestResult

def _run_single_input_tuning_step(ate, interaction_callback, mode, input_dbm, _target, tol, label, step_index):
    results = []
    
    channel_idx = 0 if mode.lower() == "body" else 1
    current_val = -999.0

    # Override target based on mode, regardless of input_dbm
    if mode.lower() == "body":
        target = -4.5
        vpp_mv = 132
    elif mode.lower() == "head":
        target = -13.5
        vpp_mv = 47
    else:
        # Fallback to provided target if unknown mode
        target = _target
        p_w = (10 ** (target / 10.0)) * 0.001
        vpp_mv = 2 * math.sqrt(2) * math.sqrt(p_w * 50) * 1000
    
    # 1. Setup and Measure (Initial)
    vals = None
    try:
        if hasattr(ate, "input_tuning"):
            try:
                vals = ate.input_tuning(mode, input_dbm)
                current_val = vals[channel_idx]
            except Exception:
                pass
        
        # 2. Loop for manual adjustment
        while True:
            # Check if within spec
            diff = abs(current_val - target)
            in_spec = diff <= tol
            status_str = "PASS" if in_spec else "FAIL"

            # Check channel difference
            diff_error = ""
            if vals and len(vals) >= 2:
                ch_diff = abs(vals[0] - vals[1])
                if ch_diff > 0.2:
                    diff_error = f"\n\nERREUR CRITIQUE: Différence entre canaux > 0.2dB ({ch_diff:.2f}dB)!\nL'entrée de la carte est défectueuse."
                    in_spec = False
                    status_str = "FAIL (DIFF)"
            
            msg = (f"{label}\n"
                   f"Sortie cible : {target} +/- {tol} dBm ({vpp_mv:.0f} mVpp)\n"
                   f"Sortie actuelle : {current_val:.2f} dBm ({status_str}){diff_error}\n\n"
                   f"Veuillez ajuster le gain du mode {mode.upper()} manuellement pour que l'osicilloscope mesure {vpp_mv:.0f} mVpp.\n"
                   "Cliquez sur 'Mesurer' pour mesurer à nouveau.\n"
                   "Cliquez sur 'Continuer' pour terminer cette étape.")
            
            retry = False
            if interaction_callback:
                retry = interaction_callback(msg)
            
            if retry:
                if hasattr(ate, "input_tuning"):
                    try:
                        vals = ate.input_tuning(mode, input_dbm)
                        current_val = vals[channel_idx]
                    except Exception:
                        pass
                continue
            else:
                break
    finally:
        # Ensure signals are turned off after the step (whether passed, failed, or aborted)
        if ate:
            if hasattr(ate, "rf") and hasattr(ate.rf, "poweroff"):
                try: ate.rf.poweroff()
                except: pass
            if hasattr(ate, "en") and hasattr(ate.en, "poweroff"):
                try: ate.en.poweroff()
                except: pass
            if hasattr(ate, "comm") and hasattr(ate.comm, "standby"):
                try: ate.comm.standby()
                except: pass
    
    # Final check for this step
    in_spec = abs(current_val - target) <= tol
    
    # Re-check channel difference on exit
    if vals and len(vals) >= 2:
        if abs(vals[0] - vals[1]) > 0.2:
            in_spec = False
        
    results.append(TestResult(
        test_id=f"12001-{step_index}",
        label=label,
        value="PASS" if in_spec else "FAIL",
        unit="",
        min_spec=None,
        max_spec=None,
        status="OK" if in_spec else "FAIL"
    ))
    
    return results, in_spec

def run_input_tuning_step_1(ate, interaction_callback=None):
    return _run_single_input_tuning_step(ate, interaction_callback, "body", -4, -4.5, 0.5, "Mode Body, Entrée -4dBm", 1)

def run_input_tuning_step_2(ate, interaction_callback=None):
    return _run_single_input_tuning_step(ate, interaction_callback, "head", -4, -13.5, 0.5, "Mode Head, Entrée -4dBm", 2)

def run_input_tuning_step_3(ate, interaction_callback=None):
    return _run_single_input_tuning_step(ate, interaction_callback, "body", 10, -4.5, 0.5, "Mode Body, Entrée +10dBm", 3)

def run_input_tuning_step_4(ate, interaction_callback=None):
    return _run_single_input_tuning_step(ate, interaction_callback, "head", 10, -13.5, 0.5, "Mode Head, Entrée +10dBm", 4)

def run_input_tuning_step_0dbm_body(ate, interaction_callback=None):
    return _run_single_input_tuning_step(ate, interaction_callback, "body", 0, -4.5, 0.5, "Mode Body, Entrée 0dBm", 5)

def run_input_tuning_step_0dbm_head(ate, interaction_callback=None):
    return _run_single_input_tuning_step(ate, interaction_callback, "head", 0, -13.5, 0.5, "Mode Head, Entrée 0dBm", 6)

def run_input_conditional_board_tuning(ate, interaction_callback=None):
    results = []
    all_steps_passed = True
    
    steps = [
        run_input_tuning_step_1,
        run_input_tuning_step_2,
        run_input_tuning_step_3,
        run_input_tuning_step_4,
        run_input_tuning_step_0dbm_body,
        run_input_tuning_step_0dbm_head,
    ]
    
    for step_func in steps:
        step_results, step_ok = step_func(ate, interaction_callback)
        results.extend(step_results)
        if not step_ok:
            all_steps_passed = False
            
    # Final Result for Test ID 12001
    status = "OK" if all_steps_passed else "FAIL"
    val = "PASS" if all_steps_passed else "FAIL"
    
    # create_test_result will fetch label and unit from specs (INPUT_COND_SPECS)
    res, _ = create_test_result("12001", "", val, "")
    res.status = status
    results.append(res)
    
    return results, all_steps_passed
