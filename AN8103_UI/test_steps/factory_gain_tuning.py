from .test_result import TestResult


def _gain_in_spec(measured, target, tol):
    return measured is not None and abs(measured - target) <= tol


def _gain_configure_input(ate, mode, input_dbm):
    if ate is None:
        return True
    try:
        # Configure Switch Matrix
        if hasattr(ate, "sw") and hasattr(ate.sw, "config"):
            ate.sw.config(f"scope_{mode}")

        # Configure Scope
        if hasattr(ate, "scope") and hasattr(ate.scope, "config"):
            ate.scope.config("power")

        # Configure Unblanking Generator (EN) - 1ms period, 0.4ms duty (matching gain_tuning)
        if hasattr(ate, "en") and hasattr(ate.en, "config") and hasattr(ate.en, "operate"):
            ate.en.config("1", "0.4")
            ate.en.operate()

        # Configure RF Generator - Gated mode (matching gain_tuning)
        if hasattr(ate, "rf") and hasattr(ate.rf, "config") and hasattr(ate.rf, "operate"):
            ate.rf.config(str(input_dbm), "gated")
            ate.rf.operate()

        if hasattr(ate, "comm"):
            try:
                ate.comm.standby()
            except Exception:
                pass
            if mode == "head" and hasattr(ate.comm, "head"):
                ate.comm.head()
            elif hasattr(ate.comm, "body"):
                ate.comm.body()
        
        return True
    except Exception:
        return False


def _gain_ate_measure(ate, mode):
    if ate is not None and hasattr(ate, "gain_tuning_power_measure"):
        try:
            return float(ate.gain_tuning_power_measure(mode))
        except Exception:
            return None
    return None


def _gain_normalize_response(response, last_measured):
    if isinstance(response, dict):
        action = response.get("action", "measure")
        measured = response.get("measured_dbm", last_measured)
        try:
            measured = float(measured) if measured is not None else None
        except Exception:
            measured = last_measured
        return action, measured
    if isinstance(response, bool):
        return ("measure", last_measured) if response else ("continue", last_measured)
    return "continue", last_measured


def _run_gain_stage(ate, interaction_callback, stage_id, title, instruction, mode, target_dbm, tol=0.2, required_count=1, allow_manual_measure=True):
    measured = None
    stable_count = 0
    allow_auto_measure = ate is not None and hasattr(ate, "gain_tuning_power_measure")
    
    # If no interaction callback, just run one measurement
    if not interaction_callback:
        measured = _gain_ate_measure(ate, mode)
        is_ok = _gain_in_spec(measured, target_dbm, tol)
        stable_count = required_count if is_ok else 0
        return measured, stable_count >= required_count, False, stable_count

    while True:
        # ATE measurement
        ate_val = None
        if allow_auto_measure:
            ate_val = _gain_ate_measure(ate, mode)

        # If manual measure is NOT allowed (e.g. HEAD), we treat the ATE value as the primary measurement
        if not allow_manual_measure and ate_val is not None:
            measured = ate_val

        # Initial validation logic (pre-interaction)
        ate_ok = _gain_in_spec(ate_val, target_dbm, tol) if ate_val is not None else False
        
        if allow_manual_measure:
            # Note: 'measured' here refers to the manually entered value
            manual_ok = _gain_in_spec(measured, target_dbm, tol) if measured is not None else False
            
            # Dual validation requirement: Both Manual and ATE must be in spec
            both_ok = manual_ok and ate_ok
            
            status = "OK" if both_ok else "HORS SPEC"
            if not manual_ok and not ate_ok:
                 status = "MANUAL & ATE FAIL"
            elif not manual_ok:
                 status = "MANUAL FAIL"
            elif not ate_ok:
                 status = "ATE FAIL"
        else:
            # For HEAD (or other auto-only steps), only ATE validation is required
            both_ok = ate_ok
            status = "OK" if both_ok else "ATE FAIL"

        # Update instruction to show ATE value if available for visual comparison
        current_instruction = instruction
        if ate_val is not None:
             current_instruction += f"\nATE Measurement: {ate_val:.2f} dBm"

        response = interaction_callback({
            "type": "step6_gain_adjust",
            "stage": stage_id,
            "title": title,
            "instruction": current_instruction,
            "target_dbm": target_dbm,
            "tolerance_db": tol,
            "measured_dbm": measured,  # This is the manual value (or ATE value if manual disabled)
            "ate_measured_dbm": ate_val, # Pass ATE value for UI display
            "status": status,
            "stable_count": stable_count,
            "required_count": required_count,
            "allow_auto_measure": allow_auto_measure,
            "allow_manual_measure": allow_manual_measure,
        })
        
        action, new_manual_val = _gain_normalize_response(response, measured)
        
        if action == "abort":
            return measured, False, True, stable_count
            
        # Update manual measurement if changed
        if new_manual_val is not None:
            measured = new_manual_val

        # Re-evaluate conditions after user input
        manual_ok = _gain_in_spec(measured, target_dbm, tol)
        # We need to re-read ATE? ideally yes, but for now use the one from top of loop or let next loop handle it
        # If user clicked "measure", we loop back and re-read ATE.
        
        if action in ("measure", "auto_measure"):
            # We loop back, which will trigger new ATE read
            # Reset stable count? Or increment? 
            # The original logic incremented stable_count if "is_ok".
            # Here "is_ok" implies both are good.
            # But we are at end of loop, we haven't re-read ATE yet for the "next" state.
            # actually, 'ate_val' is fresh from this loop iteration.
            
            if both_ok:
                stable_count += 1
            else:
                stable_count = 0
            continue
            
        if action == "continue":
            # Only allow continue if both are valid
            if both_ok and stable_count >= required_count:
                return measured, True, False, stable_count
            
            # If conditions met but user just clicked continue without a specific "measure" click sequence
            # (e.g. required_count=1), we accept if currently valid
            if required_count <= 1 and both_ok:
                 return measured, True, False, 1
                 
            # Otherwise, ignore continue or warn? 
            # The loop continues, effectively ignoring the click until conditions met
            pass


def _run_gain_subtest(ate, interaction_callback, *, step_id, stage_id, title, label, mode, input_dbm, target_dbm, tol=0.2, required_count=1, allow_manual_measure=True):
    results = []
    try:
        if not _gain_configure_input(ate, mode, input_dbm):
            results.append(TestResult(step_id, f"{label} - configuration", "FAIL", "", None, None, "FAIL"))
            return results, False
        
        if required_count > 1:
            instruction = f"{label}: entrée {input_dbm:.1f} dBm, cible {target_dbm:.1f} dBm ±{tol:.1f} dB, {required_count} mesures consécutives valides."
        else:
            instruction = f"{label}: entrée {input_dbm:.1f} dBm, cible {target_dbm:.1f} dBm ±{tol:.1f} dB, validation immédiate."
            
        measured, ok, aborted, hits = _run_gain_stage(ate, interaction_callback, stage_id, title, instruction, mode, target_dbm, tol, required_count, allow_manual_measure)
        status = "OK" if ok and not aborted else "FAIL"
        
        results.append(TestResult(step_id, f"{label} - sortie", measured if measured is not None else "N/A", "dBm", target_dbm - tol, target_dbm + tol, status))
        if measured is not None:
            gain_val = measured - input_dbm
            results.append(TestResult(f"{step_id}G", f"{label} - gain", round(gain_val, 3), "dB", None, None, status))
        
        # Only show consecutive count if it matters (more than 1 required)
        if required_count > 1:
            results.append(TestResult(f"{step_id}H", f"{label} - mesures consécutives", hits, "count", required_count, None, status))
            
        return results, ok and not aborted
    finally:
        # Ensure signals are turned off after the subtest
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


def run_factory_gain_pre_body(ate, interaction_callback=None):
    results, ok = _run_gain_subtest(
        ate,
        interaction_callback,
        step_id="15001",
        stage_id="factory_pre_body",
        title="Pré-réglage BODY",
        label="Pré-réglage BODY",
        mode="body",
        input_dbm=0.0,
        target_dbm=68.5,
    )
    if ate is not None and results:
        for r in results:
            if r.test_id == "15001" and isinstance(r.value, (int, float)):
                ate.step6_pre_body_output_dbm = float(r.value)
    return results, ok


def run_factory_gain_body_final(ate, interaction_callback=None):
    results, ok = _run_gain_subtest(
        ate,
        interaction_callback,
        step_id="15002",
        stage_id="factory_body_final",
        title="Réglage final BODY",
        label="Réglage final BODY",
        mode="body",
        input_dbm=3.5,
        target_dbm=72.0,
    )
    if ate is not None and results:
        for r in results:
            if r.test_id == "15002" and isinstance(r.value, (int, float)):
                ate.step6_body_output_dbm = float(r.value)
            if r.test_id == "15002G" and isinstance(r.value, (int, float)):
                ate.step6_body_gain_db = float(r.value)
    return results, ok


def run_factory_gain_head_final(ate, interaction_callback=None):
    results, ok = _run_gain_subtest(
        ate,
        interaction_callback,
        step_id="15003",
        stage_id="factory_head_final",
        title="Réglage final HEAD",
        label="Réglage final HEAD",
        mode="head",
        input_dbm=3.5,
        target_dbm=63.5,
        allow_manual_measure=False,
    )
    if ate is not None and results:
        for r in results:
            if r.test_id == "15003" and isinstance(r.value, (int, float)):
                ate.step6_head_output_dbm = float(r.value)
            if r.test_id == "15003G" and isinstance(r.value, (int, float)):
                ate.step6_head_gain_db = float(r.value)
    return results, ok


def run_configuration_finale(ate, interaction_callback=None):
    lines = []
    values = {}
    r1, ok1 = run_factory_gain_pre_body(ate, interaction_callback)
    r2, ok2 = run_factory_gain_body_final(ate, interaction_callback) if ok1 else ([], False)
    r3, ok3 = run_factory_gain_head_final(ate, interaction_callback) if ok2 else ([], False)
    all_results = r1 + r2 + r3
    for r in all_results:
        lines.append(f"{r.label}: {r.value} {r.unit} [{r.status}]")
    values["step6_pre_body_output_dbm"] = getattr(ate, "step6_pre_body_output_dbm", None)
    values["step6_body_output_dbm"] = getattr(ate, "step6_body_output_dbm", None)
    values["step6_head_output_dbm"] = getattr(ate, "step6_head_output_dbm", None)
    values["step6_body_gain_db"] = getattr(ate, "step6_body_gain_db", None)
    values["step6_head_gain_db"] = getattr(ate, "step6_head_gain_db", None)
    return lines, (ok1 and ok2 and ok3), values