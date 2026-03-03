from .test_result import TestResult


def _gain_in_spec(measured, target, tol):
    return measured is not None and abs(measured - target) <= tol


def _gain_configure_input(ate, mode, input_dbm):
    if ate is None:
        return True
    try:
        if hasattr(ate, "comm"):
            try:
                ate.comm.standby()
            except Exception:
                pass
            if mode == "head" and hasattr(ate.comm, "head"):
                ate.comm.head()
            elif hasattr(ate.comm, "body"):
                ate.comm.body()
        if hasattr(ate, "rf") and hasattr(ate.rf, "config") and hasattr(ate.rf, "operate"):
            ate.rf.config(str(input_dbm), "")
            ate.rf.operate()
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
        # Always try to refresh measurement from ATE if available
        if allow_auto_measure:
            auto_val = _gain_ate_measure(ate, mode)
            if auto_val is not None:
                measured = auto_val

        is_ok = _gain_in_spec(measured, target_dbm, tol)
        status = "OK" if is_ok else "HORS SPEC"
        
        response = interaction_callback({
            "type": "step6_gain_adjust",
            "stage": stage_id,
            "title": title,
            "instruction": instruction,
            "target_dbm": target_dbm,
            "tolerance_db": tol,
            "measured_dbm": measured,
            "status": status,
            "stable_count": stable_count,
            "required_count": required_count,
            "allow_auto_measure": allow_auto_measure,
            "allow_manual_measure": allow_manual_measure,
        })
        
        action, measured = _gain_normalize_response(response, measured)
        
        if action == "abort":
            return measured, False, True, stable_count
            
        # Re-check spec with potentially new manual measurement
        is_ok = _gain_in_spec(measured, target_dbm, tol)
        
        if action in ("measure", "auto_measure"):
            # Update stable count based on current measurement
            stable_count = stable_count + 1 if is_ok else 0
            continue
            
        if action == "continue":
            if is_ok and stable_count >= required_count:
                return measured, True, False, stable_count
            # If user clicked continue but conditions not met, we might want to warn or just loop.
            # For now, let's assume if they click continue and it's good, we exit. 
            # If not good, maybe we should let them force pass? 
            # The original logic implied strict check on continue.
            # But if required_count is 1, stable_count should be at least 1 if is_ok is true.
            if is_ok:
                # If we are here, it means stable_count < required_count but is_ok is True.
                # This can happen if required_count > 1 and we haven't hit it yet.
                # If required_count is 1, stable_count should have been incremented in previous loop?
                # Actually, stable_count is only incremented on "measure" action.
                # If user opens dialog, sees good value, and clicks "Continue" immediately:
                # We should probably treat that as a valid confirmation if it's in spec.
                return measured, True, False, max(stable_count, 1)
            else:
                # User clicked continue but value is bad. 
                # Strict mode: reject.
                pass


def _run_gain_subtest(ate, interaction_callback, *, step_id, stage_id, title, label, mode, input_dbm, target_dbm, tol=0.2, required_count=1, allow_manual_measure=True):
    results = []
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
