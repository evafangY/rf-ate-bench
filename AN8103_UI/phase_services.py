import math
from dataclasses import dataclass
from typing import Optional, Union, List

@dataclass
class TestResult:
    test_id: str
    label: str
    value: Union[float, str]
    unit: str
    min_spec: Optional[float]
    max_spec: Optional[float]
    status: str  # "PASS", "FAIL", "INFO"

from .error_codes import ERROR_CODES, ERROR_HINTS
from .specs import PERFORMANCE_SPECS, DIAGNOSTIC_SPECS, DIAGNOSTIC_EXCLUDED_BIASES

def run_diagnostic(ate):
    lines = []
    ok = True
    spec = DIAGNOSTIC_SPECS.get("bias")
    bias_min = spec[2] if spec else 175
    bias_max = spec[3] if spec else 225
    lines.append("<h3>Diagnostic summary</h3>")
    try:
        if hasattr(ate, "diagnostics"):
            ate.diagnostics()
    except AttributeError:
        pass
    state = getattr(getattr(ate, "comm", None), "state", "N/A")
    master = getattr(ate, "master", None)
    slave = getattr(ate, "slave", None)
    master_140 = getattr(master, "alim_140", "N/A")
    master_48 = getattr(master, "alim_48", "N/A")
    master_p15 = getattr(master, "alim_p15", "N/A")
    master_m15 = getattr(master, "alim_m15", "N/A")
    master_fault = getattr(master, "fault", "N/A")
    master_error_dec = getattr(master, "error", None)
    master_gain = getattr(master, "Gai", "N/A")
    slave_140 = getattr(slave, "alim_140", "N/A")
    slave_48 = getattr(slave, "alim_48", "N/A")
    slave_p15 = getattr(slave, "alim_p15", "N/A")
    slave_m15 = getattr(slave, "alim_m15", "N/A")
    slave_fault = getattr(slave, "fault", "N/A")
    slave_error_dec = getattr(slave, "error", None)
    slave_gain = getattr(slave, "Gai", "N/A")
    state_raw = str(state).strip()
    try:
        state_val = int(state_raw)
    except Exception:
        state_val = state_raw
    state_text = {0: "Poweroff", 1: "Standby", 3: "Operate"}.get(state_val, "Unknown")
    
    if isinstance(state_val, int) and state_val not in (1, 3):
        ok = False
        lines.append("Amp state is not Standby/Operate.")

    # Fault is a 0/1 flag; when 1, decode error code (decimal from ATE) to HEX and map
    def normalize_fault(val):
        try:
            return int(str(val).strip())
        except Exception:
            return 0
    m_fault_flag = normalize_fault(master_fault)
    s_fault_flag = normalize_fault(slave_fault)
    def dec_to_hex_str(v):
        try:
            return format(int(str(v).strip()), "02X")
        except Exception:
            return ""
    master_error_hex = dec_to_hex_str(master_error_dec) if m_fault_flag == 1 else ""
    slave_error_hex = dec_to_hex_str(slave_error_dec) if s_fault_flag == 1 else ""
    master_error_text = ERROR_CODES.get(master_error_hex, "") if master_error_hex else ""
    master_error_hint = ERROR_HINTS.get(master_error_hex, "") if master_error_hex else ""
    slave_error_text = ERROR_CODES.get(slave_error_hex, "") if slave_error_hex else ""
    slave_error_hint = ERROR_HINTS.get(slave_error_hex, "") if slave_error_hex else ""

    bias_names = (
        [f"biasQ{i}" for i in range(3, 11)]
        + [f"biasQ{i}" for i in range(11, 19)]
        + [f"biasQ{i}" for i in range(19, 27)]
        + ["biasQ27", "biasQ28", "biasQ31", "biasQ32", "biasQ33", "biasQ34", "biasQ35"]
    )
    excluded = set(DIAGNOSTIC_EXCLUDED_BIASES or [])
    bias_names = [n for n in bias_names if n not in excluded]
    biases_master = {}
    alarm = False
    for name in bias_names:
        if hasattr(master, name):
            val = getattr(master, name)
            biases_master[name] = val
            if val < bias_min or val > bias_max:
                alarm = True

    biases_slave = {}
    for name in bias_names:
        if hasattr(slave, name):
            val = getattr(slave, name)
            biases_slave[name] = val
            if val < bias_min or val > bias_max:
                alarm = True

    if alarm:
        ok = False
        lines.append("Bias alarm: one or more values out of range.")
    if m_fault_flag == 1 or s_fault_flag == 1:
        ok = False
        lines.append("Fault active: please investigate error code before proceeding.")
    
    lines.append("Diagnostics data collected.")

    values = {
        "state": state,
        "state_text": state_text,
        "master": {
            "alim_140": master_140,
            "alim_48": master_48,
            "alim_p15": master_p15,
            "alim_m15": master_m15,
            "fault": m_fault_flag,
            "error_code_hex": master_error_hex,
            "error_text": master_error_text,
            "error_hint": master_error_hint,
            "gain": master_gain,
            "biases": biases_master,
        },
        "slave": {
            "alim_140": slave_140,
            "alim_48": slave_48,
            "alim_p15": slave_p15,
            "alim_m15": slave_m15,
            "fault": s_fault_flag,
            "error_code_hex": slave_error_hex,
            "error_text": slave_error_text,
            "error_hint": slave_error_hint,
            "gain": slave_gain,
            "biases": biases_slave,
        },
        "bias_alarm": alarm,
    }
    return lines, ok, values


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


def run_power_module_gain_simulation(ate=None):
    lines = []
    ok = True
    lines.append("Démarrage du réglage du gain du module de puissance.")
    results = []
    if ate is None:
        ok = False
        lines.append("Instance ATE manquante pour le réglage du gain.")
    elif hasattr(ate, "gain_tuning"):
        try:
            ate.gain_tuning()
            lines.append("Réglage du gain du module de puissance terminé.")
        except Exception as e:
            ok = False
            lines.append(f"Échec du réglage du gain du module de puissance : {e}")
    else:
        ok = False
        lines.append("Fonction de réglage du gain indisponible dans AN8103_lib.")
    if hasattr(ate, "poweroff"):
        try:
            ate.poweroff()
        except Exception:
            pass
    status = "PASS" if ok else "FAIL"
    results.append(
        TestResult(
            test_id="GAIN_TUNING",
            label="Réglage du gain du module de puissance",
            value=status,
            unit="",
            min_spec=None,
            max_spec=None,
            status=status,
        )
    )
    return results, ok


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
    
    results.append(TestResult(
        test_id="12001",
        label="Gain/attenuation adjustment range (-10 to +4 dB)",
        value="PASS" if all_steps_passed else "FAIL",
        unit="", # Binary/Boolean result
        min_spec=None,
        max_spec=None,
        status=status
    ))
    
    return results, all_steps_passed


def run_performance_test(ate):
    lines = []
    ok = True
    
    # Try to run the performance test on ATE, catching any crashes
    test_exception = None
    if hasattr(ate, "performance_test"):
        try:
            ate.performance_test()
        except Exception as e:
            test_exception = str(e)
            ok = False
            lines.append(f"Erreur critique pendant l'exécution du test de performance: {e}")
    else:
        lines.append("Fonction de test de performance non disponible dans AN8103_lib.")
        ok = False
        return lines, ok
    
    results = []
    def add_result(attr, test_id, label, unit):
        # Default values if attribute is missing
        val = "N/A"
        status = "FAIL"
        spec_min = None
        spec_max = None
        
        # Get spec info first
        spec = PERFORMANCE_SPECS.get(test_id)
        if spec:
            label = spec[0]
            unit = spec[1]
            spec_min = spec[2]
            spec_max = spec[3]

        if hasattr(ate, attr):
            val = getattr(ate, attr)
            # If val is None, treat as missing/fail
            if val is None:
                val = "N/A"
                status = "FAIL"
            else:
                # Check against specs
                status = "OK"
                if spec_min is not None and val < spec_min:
                    status = "FAIL"
                if spec_max is not None and val > spec_max:
                    status = "FAIL"
        else:
            # Attribute missing -> FAIL (CRASH/MISSING)
            status = "FAIL"
            val = "MISSING"
            
        results.append(TestResult(
            test_id=test_id,
            label=label,
            value=val,
            unit=unit,
            min_spec=spec_min,
            max_spec=spec_max,
            status=status
        ))

    add_result("test_id_13301", "13301", "Single pulse drop", "dB")
    add_result("test_id_13302", "13302", "Gain inter pulse stability", "dB")
    add_result("test_id_13303", "13303", "Phase inter pulse stability", "deg")
    add_result("test_id_12007", "12007", "Input VSWR", ":1")
    add_result("test_id_13101", "13101", "Body Bandwidth (±275kHz)", "dB")
    add_result("test_id_13102", "13102", "Head Bandwidth (±275kHz)", "dB")
    add_result("test_id_13103", "13103", "Body output power nominal", "dBm")
    add_result("test_id_13104", "13104", "Head output power nominal", "dBm")
    add_result("test_id_13105", "13105", "Body output margin", "dB")
    add_result("test_id_13106", "13106", "Body gain (output-input)", "dB")
    add_result("test_id_13107", "13107", "Head delta gain", "dB")
    add_result("test_id_13108", "13108", "Seq1 body output power variation", "%")
    add_result("test_id_13109", "13109", "Seq2 body output power variation", "%")
    add_result("test_id_13110", "13110", "Seq3 body output power variation", "%")
    add_result("test_id_13111", "13111", "Seq4 body output power variation", "%")
    add_result("test_id_13112", "13112", "Seq5 body output power variation", "%")
    add_result("test_id_13113", "13113", "Seq6 body output power variation", "%")
    add_result("test_id_13114", "13114", "Seq7 body output power variation", "%")
    add_result("test_id_13115", "13115", "Seq8 body output power variation", "%")
    add_result("test_id_13201", "13201", "Harmonic output", "dBc")
    add_result("test_id_13204", "13204", "Unblanked output noise power broad spectrum", "dBm/Hz")
    add_result("test_id_13205", "13205", "Fidelity gain non linearity -40 to 0dBm", "dB")
    add_result("test_id_13206", "13206", "Fidelity differential gain -40 to -3dBm", "dB/dB")
    add_result("test_id_13207", "13207", "Fidelity differential gain -3 to -1dBm", "dB/dB")
    add_result("test_id_13208", "13208", "Fidelity differential gain -1 to 0dBm", "dB/dB")
    add_result("test_id_13209", "13209", "Fidelity phase non linearity -40 to 0dBm", "deg")
    add_result("test_id_13210", "13210", "Fidelity differential phase -40 to -3dBm", "deg/dB")
    add_result("test_id_13211", "13211", "Fidelity differential phase -3 to -1dBm", "deg/dB")
    add_result("test_id_13212", "13212", "Fidelity differential phase -1 to 0dBm", "deg/dB")
    add_result("test_id_13213", "13213", "Fidelity gain non linearity 0 to -40dBm", "dB")
    add_result("test_id_13214", "13214", "Fidelity differential gain -3 to -40dBm", "dB/dB")
    add_result("test_id_13215", "13215", "Fidelity differential gain -1 to -3dBm", "dB/dB")
    add_result("test_id_13216", "13216", "Fidelity differential gain 0 to -1dBm", "dB/dB")
    add_result("test_id_13217", "13217", "Fidelity phase non linearity 0 to -40dBm", "deg")
    add_result("test_id_13218", "13218", "Fidelity differential phase -3 to -40dBm", "deg/dB")
    add_result("test_id_13219", "13219", "Fidelity differential phase -1 to -3dBm", "deg/dB")
    add_result("test_id_13220", "13220", "Fidelity differential phase 0 to -1dBm", "deg/dB")
    
    if not results:
        ok = False
        lines.append("Aucun résultat de performance n'a été renvoyé par l'ATE.")
        # values = {}
        return lines, ok
    
    if test_exception:
        results.insert(0, TestResult(
            test_id="CRASH",
            label=f"Erreur critique: {test_exception}",
            value="ERROR",
            unit="",
            min_spec=None,
            max_spec=None,
            status="FAIL"
        ))

    # Check overall status
    if any(r.status == "FAIL" for r in results):
        ok = False

    return results, ok


def _step6_in_spec(measured, target, tol):
    return measured is not None and abs(measured - target) <= tol


def _step6_configure_input(ate, mode, input_dbm):
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


def _step6_ate_measure(ate, mode):
    if ate is not None and hasattr(ate, "gain_tuning_power_measure"):
        try:
            return float(ate.gain_tuning_power_measure(mode))
        except Exception:
            return None
    return None


def _step6_normalize_response(response, last_measured):
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


def _run_step6_stage(ate, interaction_callback, stage_id, title, instruction, mode, target_dbm, tol=0.2, required_count=3):
    measured = None
    stable_count = 0
    allow_auto_measure = ate is not None and hasattr(ate, "gain_tuning_power_measure")
    if not interaction_callback:
        measured = _step6_ate_measure(ate, mode)
        stable_count = required_count if _step6_in_spec(measured, target_dbm, tol) else 0
        return measured, stable_count >= required_count, False, stable_count
    while True:
        status = "OK" if _step6_in_spec(measured, target_dbm, tol) else "HORS SPEC"
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
        })
        action, measured = _step6_normalize_response(response, measured)
        if action == "abort":
            return measured, False, True, stable_count
        if action == "auto_measure":
            auto_val = _step6_ate_measure(ate, mode)
            if auto_val is not None:
                measured = auto_val
        if action in ("measure", "auto_measure"):
            stable_count = stable_count + 1 if _step6_in_spec(measured, target_dbm, tol) else 0
            continue
        if action == "continue" and _step6_in_spec(measured, target_dbm, tol) and stable_count >= required_count:
            return measured, True, False, stable_count


def _run_step6_subtest(ate, interaction_callback, *, step_id, stage_id, title, label, mode, input_dbm, target_dbm, tol=0.2, required_count=3):
    results = []
    if not _step6_configure_input(ate, mode, input_dbm):
        results.append(TestResult(step_id, f"{label} - configuration", "FAIL", "", None, None, "FAIL"))
        return results, False
    instruction = f"{label}: entrée {input_dbm:.1f} dBm, cible {target_dbm:.1f} dBm ±{tol:.1f} dB, {required_count} mesures consécutives valides."
    measured, ok, aborted, hits = _run_step6_stage(ate, interaction_callback, stage_id, title, instruction, mode, target_dbm, tol, required_count)
    status = "OK" if ok and not aborted else "FAIL"
    results.append(TestResult(step_id, f"{label} - sortie", measured if measured is not None else "N/A", "dBm", target_dbm - tol, target_dbm + tol, status))
    if measured is not None:
        gain_val = measured - input_dbm
        results.append(TestResult(f"{step_id}G", f"{label} - gain", round(gain_val, 3), "dB", None, None, status))
    results.append(TestResult(f"{step_id}H", f"{label} - mesures consécutives", hits, "count", required_count, None, status))
    return results, ok and not aborted


def run_factory_gain_step_1_pre_body(ate, interaction_callback=None):
    results, ok = _run_step6_subtest(
        ate,
        interaction_callback,
        step_id="15001",
        stage_id="factory_pre_body",
        title="Step 6 - Pré-réglage BODY",
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


def run_factory_gain_step_2_body_final(ate, interaction_callback=None):
    results, ok = _run_step6_subtest(
        ate,
        interaction_callback,
        step_id="15002",
        stage_id="factory_body_final",
        title="Step 6 - Réglage final BODY",
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


def run_factory_gain_step_3_head_final(ate, interaction_callback=None):
    results, ok = _run_step6_subtest(
        ate,
        interaction_callback,
        step_id="15003",
        stage_id="factory_head_final",
        title="Step 6 - Réglage final HEAD",
        label="Réglage final HEAD",
        mode="head",
        input_dbm=3.5,
        target_dbm=63.5,
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
    r1, ok1 = run_factory_gain_step_1_pre_body(ate, interaction_callback)
    r2, ok2 = run_factory_gain_step_2_body_final(ate, interaction_callback) if ok1 else ([], False)
    r3, ok3 = run_factory_gain_step_3_head_final(ate, interaction_callback) if ok2 else ([], False)
    all_results = r1 + r2 + r3
    for r in all_results:
        lines.append(f"{r.label}: {r.value} {r.unit} [{r.status}]")
    values["step6_pre_body_output_dbm"] = getattr(ate, "step6_pre_body_output_dbm", None)
    values["step6_body_output_dbm"] = getattr(ate, "step6_body_output_dbm", None)
    values["step6_head_output_dbm"] = getattr(ate, "step6_head_output_dbm", None)
    values["step6_body_gain_db"] = getattr(ate, "step6_body_gain_db", None)
    values["step6_head_gain_db"] = getattr(ate, "step6_head_gain_db", None)
    return lines, (ok1 and ok2 and ok3), values


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


def build_subtest_registry(ate, interaction_callback=None):
    return {
        "run_input_tuning_step_1": lambda: run_input_tuning_step_1(ate, interaction_callback),
        "run_input_tuning_step_2": lambda: run_input_tuning_step_2(ate, interaction_callback),
        "run_input_tuning_step_3": lambda: run_input_tuning_step_3(ate, interaction_callback),
        "run_input_tuning_step_4": lambda: run_input_tuning_step_4(ate, interaction_callback),
        "run_input_tuning_step_0dbm_body": lambda: run_input_tuning_step_0dbm_body(ate, interaction_callback),
        "run_input_tuning_step_0dbm_head": lambda: run_input_tuning_step_0dbm_head(ate, interaction_callback),
        "run_factory_gain_step_1_pre_body": lambda: run_factory_gain_step_1_pre_body(ate, interaction_callback),
        "run_factory_gain_step_2_body_final": lambda: run_factory_gain_step_2_body_final(ate, interaction_callback),
        "run_factory_gain_step_3_head_final": lambda: run_factory_gain_step_3_head_final(ate, interaction_callback),
    }
