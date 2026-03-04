from AN8103_UI.specs import DIAGNOSTIC_SPECS, DIAGNOSTIC_EXCLUDED_BIASES, ZERO_TARGET_BIAS_TOLERANCE
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
    
    # Get master/slave objects safely
    master = getattr(ate, "master", None)
    slave = getattr(ate, "slave", None)
    comm = getattr(ate, "comm", None)
    state = getattr(comm, "state", "N/A")
    
    # Helper to get attribute safely
    def get_val(obj, attr, default="N/A"):
        return getattr(obj, attr, default)

    # State check
    state_raw = str(state).strip()
    try:
        state_val = int(state_raw)
    except Exception:
        state_val = state_raw
    state_text = {0: "Poweroff", 1: "Standby", 3: "Operate"}.get(state_val, "Unknown")
    
    if isinstance(state_val, int) and state_val not in (1, 3):
        ok = False
        lines.append("<font color='red'>Amp state is not Standby/Operate.</font>")

    # Check for Simulation Mode
    is_sim = False
    if hasattr(ate, "is_simulation") and ate.is_simulation:
        is_sim = True
    elif type(ate).__name__ == "FakeATE":
        is_sim = True
    
    if is_sim:
        lines.append("<font color='orange'><b>WARNING: Running in SIMULATION MODE</b></font>")
        lines.append("Values are simulated (e.g. biasQxx=200).")

    # Fault handling
    def normalize_fault(val):
        try:
            return int(str(val).strip())
        except Exception:
            return 0
            
    m_fault_flag = normalize_fault(get_val(master, "fault"))
    s_fault_flag = normalize_fault(get_val(slave, "fault"))
    
    def dec_to_hex_str(v):
        try:
            # Handle possible float or string inputs safely
            val = float(str(v).strip())
            return format(int(val), "02X")
        except Exception:
            return ""
            
    master_error_dec = get_val(master, "error", None)
    slave_error_dec = get_val(slave, "error", None)
    
    master_error_hex = dec_to_hex_str(master_error_dec) if m_fault_flag == 1 else ""
    slave_error_hex = dec_to_hex_str(slave_error_dec) if s_fault_flag == 1 else ""
    
    master_error_text = ERROR_CODES.get(master_error_hex, "") if master_error_hex else ""
    master_error_hint = ERROR_HINTS.get(master_error_hex, "") if master_error_hex else ""
    slave_error_text = ERROR_CODES.get(slave_error_hex, "") if slave_error_hex else ""
    slave_error_hint = ERROR_HINTS.get(slave_error_hex, "") if slave_error_hex else ""

    # Bias checking logic
    bias_names = (
        [f"biasQ{i}" for i in range(3, 11)]
        + [f"biasQ{i}" for i in range(11, 19)]
        + [f"biasQ{i}" for i in range(19, 27)]
        + ["biasQ27", "biasQ28", "biasQ31", "biasQ32", "biasQ33", "biasQ34", "biasQ35"]
    )
    
    excluded = set(DIAGNOSTIC_EXCLUDED_BIASES or [])
    
    def check_biases(obj):
        biases = {}
        has_alarm = False
        if obj is None:
            return biases, False
            
        for name in bias_names:
            if hasattr(obj, name):
                val = getattr(obj, name)
                biases[name] = val
                
                if name in excluded:
                    # Excluded biases should be near 0 (e.g. < 20)
                    if val > ZERO_TARGET_BIAS_TOLERANCE:
                        has_alarm = True
                elif val < bias_min or val > bias_max:
                    has_alarm = True
        return biases, has_alarm

    biases_master, alarm_master = check_biases(master)
    biases_slave, alarm_slave = check_biases(slave)
    
    alarm = alarm_master or alarm_slave

    if alarm:
        ok = False
        lines.append("<font color='red'>Bias alarm: one or more values out of range.</font>")
        
    if m_fault_flag == 1 or s_fault_flag == 1:
        ok = False
        lines.append("<font color='red'>Fault active: please investigate error code before proceeding.</font>")
        
        if m_fault_flag == 1 and master_error_hex:
            msg = f"Master Error: 0x{master_error_hex} - {master_error_text}"
            if master_error_hint:
                msg += f" ({master_error_hint})"
            lines.append(f"<font color='red'>{msg}</font>")
            
        if s_fault_flag == 1 and slave_error_hex:
            msg = f"Slave Error: 0x{slave_error_hex} - {slave_error_text}"
            if slave_error_hint:
                msg += f" ({slave_error_hint})"
            lines.append(f"<font color='red'>{msg}</font>")
    
    if ok:
        lines.append("<font color='green'>Diagnostics Passed.</font>")
    else:
        lines.append("<font color='red'>Diagnostics Failed.</font>")

    lines.append("Diagnostics data collected.")

    values = {
        "state": state,
        "state_text": state_text,
        "master_temp1": get_val(master, "temp1"),
        "master_temp2": get_val(master, "temp2"),
        "slave_temp1": get_val(slave, "temp1"),
        "slave_temp2": get_val(slave, "temp2"),
        "master": {
            "alim_140": get_val(master, "alim_140"),
            "alim_48": get_val(master, "alim_48"),
            "alim_p15": get_val(master, "alim_p15"),
            "alim_m15": get_val(master, "alim_m15"),
            "fault": m_fault_flag,
            "error_code_hex": master_error_hex,
            "error_text": master_error_text,
            "error_hint": master_error_hint,
            "gain": get_val(master, "Gai"),
            "biases": biases_master,
        },
        "slave": {
            "alim_140": get_val(slave, "alim_140"),
            "alim_48": get_val(slave, "alim_48"),
            "alim_p15": get_val(slave, "alim_p15"),
            "alim_m15": get_val(slave, "alim_m15"),
            "fault": s_fault_flag,
            "error_code_hex": slave_error_hex,
            "error_text": slave_error_text,
            "error_hint": slave_error_hint,
            "gain": get_val(slave, "Gai"),
            "biases": biases_slave,
        },
        "bias_alarm": alarm,
    }
    return lines, ok, values
