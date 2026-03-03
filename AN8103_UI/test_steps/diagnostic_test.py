from AN8103_UI.specs import DIAGNOSTIC_SPECS, DIAGNOSTIC_EXCLUDED_BIASES
from AN8103_UI.error_codes import ERROR_CODES, ERROR_HINTS

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
