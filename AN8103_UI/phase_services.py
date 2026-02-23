import datetime
from AN8103_UI.error_codes import ERROR_CODES, ERROR_HINTS, decode_error
from AN8103_UI.specs import PERFORMANCE_SPECS

def render_bias_grid(biases, columns=4):
    items = list(biases.items())
    html = []
    html.append("<table border='1' cellspacing='0' cellpadding='3'>")
    html.append("<tr>" + "".join("<th>Bias</th><th>Value</th><th>Status</th>" for _ in range(columns)) + "</tr>")
    alarm = False
    for i in range(0, len(items), columns):
        html.append("<tr>")
        chunk = items[i : i + columns]
        for name, val in chunk:
            status = "OK"
            cell_style = ""
            if val < 175 or val > 225:
                alarm = True
                status = "ALARM"
                cell_style = " style='color:red'"
            html.append(f"<td>{name}</td><td{cell_style}>{val}</td><td{cell_style}>{status}</td>")
        for _ in range(columns - len(chunk)):
            html.append("<td></td><td></td><td></td>")
        html.append("</tr>")
    html.append("</table>")
    return "".join(html), alarm


def run_diagnostic(ate):
    lines = []
    ok = True
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
    lines.append(f"<p><b>Amp state:</b> {state_val} ({state_text})</p>")
    if isinstance(state_val, int) and state_val not in (1, 3):
        ok = False
        lines.append("<p style='color:red;font-weight:bold'>Amp state is not Standby/Operate.</p>")
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
    lines.append(
        "<table border='1' cellspacing='0' cellpadding='3'>"
        "<tr><th></th><th>140V</th><th>48V</th><th>+15V</th><th>-15V</th><th>Fault</th><th>Error code</th><th>Error text</th><th>Gain</th></tr>"
        f"<tr><td>Master</td><td>{master_140}</td><td>{master_48}</td><td>{master_p15}</td>"
        f"<td>{master_m15}</td><td>{m_fault_flag}</td><td>{master_error_hex or '—'}</td><td>{master_error_text or '—'}</td><td>{master_gain}</td></tr>"
        f"<tr><td>Slave</td><td>{slave_140}</td><td>{slave_48}</td><td>{slave_p15}</td>"
        f"<td>{slave_m15}</td><td>{s_fault_flag}</td><td>{slave_error_hex or '—'}</td><td>{slave_error_text or '—'}</td><td>{slave_gain}</td></tr>"
        "</table>"
    )
    if master_error_hint or slave_error_hint:
        lines.append("<ul>")
        if master_error_hint:
            lines.append(f"<li><b>Master error hint:</b> {master_error_hint}</li>")
        if slave_error_hint:
            lines.append(f"<li><b>Slave error hint:</b> {slave_error_hint}</li>")
        lines.append("</ul>")
    lines.append("<h4>Master biases</h4>")
    bias_names = (
        [f"biasQ{i}" for i in range(3, 11)]
        + [f"biasQ{i}" for i in range(11, 19)]
        + [f"biasQ{i}" for i in range(19, 27)]
        + ["biasQ27", "biasQ28", "biasQ31", "biasQ32", "biasQ33", "biasQ34", "biasQ35"]
    )
    biases_master = {}
    alarm = False
    for name in bias_names:
        if hasattr(master, name):
            val = getattr(master, name)
            biases_master[name] = val
    grid_html_master, alarm_master = render_bias_grid(biases_master, columns=4)
    lines.append(grid_html_master)
    lines.append("<h4>Slave biases</h4>")
    biases_slave = {}
    for name in bias_names:
        if hasattr(slave, name):
            val = getattr(slave, name)
            biases_slave[name] = val
    grid_html_slave, alarm_slave = render_bias_grid(biases_slave, columns=4)
    lines.append(grid_html_slave)
    if alarm_master or alarm_slave:
        ok = False
        lines.append("<p style='color:red;font-weight:bold'>Bias alarm: one or more values out of 200 ± 25</p>")
    if m_fault_flag == 1 or s_fault_flag == 1:
        ok = False
        lines.append("<p style='color:red;font-weight:bold'>Fault active: please investigate error code before proceeding.</p>")
    lines.append("<p>Diagnostics completed.</p>")
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
            "gain": slave_gain,
            "biases": biases_slave,
        },
        "bias_alarm": alarm,
    }
    return lines, ok, values


def run_output_conditional_simulation():
    lines = []
    ok = True
    lines.append("Starting output conditional tuning (simulation).")
    lines.append("Target body output power: 50.0 dBm")
    lines.append("Target head output power: 43.0 dBm")
    body_power = 50.1
    head_power = 43.2
    lines.append(f"Measured body output: {body_power:.2f} dBm")
    lines.append(f"Measured head output: {head_power:.2f} dBm")
    lines.append("Output conditional tuning completed.")
    values = {
        "body_output_power_dbm": body_power,
        "head_output_power_dbm": head_power,
    }
    return lines, ok, values


def run_power_module_gain_simulation():
    lines = []
    ok = True
    lines.append("Starting power module gain tuning (simulation).")
    lines.append("Target gain: 69.0 dB")
    master_gain_db = 69.1
    slave_gain_db = 68.9
    lines.append(f"Master module gain: {master_gain_db:.2f} dB")
    lines.append(f"Slave module gain: {slave_gain_db:.2f} dB")
    lines.append("Power module gain tuning completed.")
    values = {
        "master_gain_db": master_gain_db,
        "slave_gain_db": slave_gain_db,
    }
    return lines, ok, values


def run_input_conditional_simulation():
    lines = []
    ok = True
    lines.append("Starting input conditional board tuning (simulation).")
    lines.append("Target input gain body: 72.0 dBm")
    lines.append("Target input gain head: 63.0 dBm")
    body_input_gain = 71.95
    head_input_gain = 63.05
    lines.append(f"Body input gain: {body_input_gain:.2f} dBm")
    lines.append(f"Head input gain: {head_input_gain:.2f} dBm")
    lines.append("Input conditional board tuning completed.")
    values = {
        "body_input_gain_dbm": body_input_gain,
        "head_input_gain_dbm": head_input_gain,
    }
    return lines, ok, values


def run_performance_test(ate):
    lines = []
    ok = True
    lines.append("<h3>Test de performance</h3>")
    if hasattr(ate, "performance_test"):
        ate.performance_test()
    else:
        lines.append("Fonction de test de performance non disponible dans AN8103_lib.")
        ok = False
        values = {}
        return lines, ok, values
    results = []
    def add_result(attr, test_id, label, unit):
        if hasattr(ate, attr):
            val = getattr(ate, attr)
            spec = PERFORMANCE_SPECS.get(test_id)
            spec_min = None
            spec_max = None
            if spec:
                label = spec[0]
                unit = spec[1]
                spec_min = spec[2]
                spec_max = spec[3]
            status = ""
            if spec_min is not None or spec_max is not None:
                ok_value = True
                if spec_min is not None and val < spec_min:
                    ok_value = False
                if spec_max is not None and val > spec_max:
                    ok_value = False
                status = "OK" if ok_value else "FAIL"
            results.append((test_id, label, val, unit, spec_min, spec_max, status))
    add_result("test_id_12007", "12007", "Input VSWR", "")
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
    if results:
        lines.append("<table border='1' cellspacing='0' cellpadding='3'>")
        lines.append("<tr><th>ID</th><th>Measurement</th><th>Value</th><th>Unit</th><th>Spec min</th><th>Spec max</th><th>Status</th></tr>")
        any_fail = False
        for test_id, label, val, unit, spec_min, spec_max, status in results:
            row_style = ""
            if status == "FAIL":
                row_style = " style='color:red;font-weight:bold'"
                any_fail = True
            elif status == "OK":
                row_style = " style='color:green'"
            min_str = "" if spec_min is None else str(spec_min)
            max_str = "" if spec_max is None else str(spec_max)
            lines.append(
                f"<tr{row_style}><td>{test_id}</td><td>{label}</td><td>{round(val, 2)}</td>"
                f"<td>{unit}</td><td>{min_str}</td><td>{max_str}</td><td>{status}</td></tr>"
            )
        lines.append("</table>")
        if any_fail:
            ok = False
            lines.append("<p style='color:red;font-weight:bold'>One or more performance measurements are out of specification.</p>")
    else:
        ok = False
        lines.append("Aucun résultat de performance n'a été renvoyé par l'ATE.")
    lines.append("<p>Test de performance terminé.</p>")
    values = {
        "13301_single_pulse_drop_db": getattr(ate, "test_id_13301", ""),
        "13201_harmonic_output_db": getattr(ate, "test_id_13201", ""),
        "13204_noise_unblanked_dbm_hz": getattr(ate, "test_id_13204", ""),
        "13101_gain_flatness_body_db": getattr(ate, "test_id_13101", ""),
        "13102_gain_flatness_head_db": getattr(ate, "test_id_13102", ""),
        "13106_body_power_dbm": getattr(ate, "test_id_13106", ""),
        "13107_head_power_dbm": getattr(ate, "test_id_13107", ""),
        "13108_stress1_gain_variation_percent": getattr(ate, "test_id_13108", ""),
        "13109_stress2_gain_variation_percent": getattr(ate, "test_id_13109", ""),
        "13110_stress3_gain_variation_percent": getattr(ate, "test_id_13110", ""),
        "13111_stress4_gain_variation_percent": getattr(ate, "test_id_13111", ""),
        "13112_stress5_gain_variation_percent": getattr(ate, "test_id_13112", ""),
    }
    return lines, ok, values


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
