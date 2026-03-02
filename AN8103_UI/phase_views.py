from .specs import DIAGNOSTIC_SPECS

def render_results_table(results):
    html = []
    html.append("<table border='1' cellspacing='0' cellpadding='3'>")
    html.append("<tr><th>ID</th><th>Mesure</th><th>Valeur</th><th>Unité</th><th>Spec min</th><th>Spec max</th><th>Statut</th></tr>")
    for r in results:
        row_style = ""
        if r.status == "FAIL":
            row_style = " style='color:red;font-weight:bold'"
        elif r.status in ("PASS", "OK"):
            row_style = " style='color:green'"
        min_str = "" if r.min_spec is None else str(r.min_spec)
        max_str = "" if r.max_spec is None else str(r.max_spec)
        val_str = f"{r.value:.2f}" if isinstance(r.value, (int, float)) else str(r.value)
        html.append(
            f"<tr{row_style}><td>{r.test_id}</td><td>{r.label}</td><td>{val_str}</td>"
            f"<td>{r.unit}</td><td>{min_str}</td><td>{max_str}</td><td>{r.status}</td></tr>"
        )
    html.append("</table>")
    return "".join(html)

def render_bias_grid(biases, columns=4):
    spec = DIAGNOSTIC_SPECS.get("bias")
    bias_min = spec[2] if spec else 175
    bias_max = spec[3] if spec else 225
    items = list(biases.items())
    html = []
    html.append("<table border='1' cellspacing='0' cellpadding='3'>")
    html.append("<tr>" + "".join("<th>Bias</th><th>Value</th><th>Status</th>" for _ in range(columns)) + "</tr>")
    
    for i in range(0, len(items), columns):
        html.append("<tr>")
        chunk = items[i : i + columns]
        for name, val in chunk:
            status = "OK"
            cell_style = ""
            if val < bias_min or val > bias_max:
                status = "ALARM"
                cell_style = " style='color:red'"
            html.append(f"<td>{name}</td><td{cell_style}>{val}</td><td{cell_style}>{status}</td>")
        for _ in range(columns - len(chunk)):
            html.append("<td></td><td></td><td></td>")
        html.append("</tr>")
    html.append("</table>")
    return "".join(html)

def render_diagnostic_report(values):
    lines = []
    lines.append("<h3>Diagnostic summary</h3>")
    
    state = values.get("state", "N/A")
    state_text = values.get("state_text", "Unknown")
    lines.append(f"<p><b>Amp state:</b> {state} ({state_text})</p>")
    
    if isinstance(state, int) and state not in (1, 3):
        lines.append("<p style='color:red;font-weight:bold'>Amp state is not Standby/Operate.</p>")

    master = values.get("master", {})
    slave = values.get("slave", {})
    
    lines.append(
        "<table border='1' cellspacing='0' cellpadding='3'>"
        "<tr><th></th><th>140V</th><th>48V</th><th>+15V</th><th>-15V</th><th>Fault</th><th>Error code</th><th>Error text</th><th>Gain</th></tr>"
        f"<tr><td>Master</td><td>{master.get('alim_140')}</td><td>{master.get('alim_48')}</td><td>{master.get('alim_p15')}</td>"
        f"<td>{master.get('alim_m15')}</td><td>{master.get('fault')}</td><td>{master.get('error_code_hex') or '—'}</td><td>{master.get('error_text') or '—'}</td><td>{master.get('gain')}</td></tr>"
        f"<tr><td>Slave</td><td>{slave.get('alim_140')}</td><td>{slave.get('alim_48')}</td><td>{slave.get('alim_p15')}</td>"
        f"<td>{slave.get('alim_m15')}</td><td>{slave.get('fault')}</td><td>{slave.get('error_code_hex') or '—'}</td><td>{slave.get('error_text') or '—'}</td><td>{slave.get('gain')}</td></tr>"
        "</table>"
    )

    master_hint = master.get("error_hint")
    slave_hint = slave.get("error_hint")
    
    if master_hint or slave_hint:
        lines.append("<ul>")
        if master_hint:
            lines.append(f"<li><b>Master error hint:</b> {master_hint}</li>")
        if slave_hint:
            lines.append(f"<li><b>Slave error hint:</b> {slave_hint}</li>")
        lines.append("</ul>")
    
    lines.append("<h4>Master biases</h4>")
    lines.append(render_bias_grid(master.get("biases", {})))
    
    lines.append("<h4>Slave biases</h4>")
    lines.append(render_bias_grid(slave.get("biases", {})))
    
    if values.get("bias_alarm"):
        spec = DIAGNOSTIC_SPECS.get("bias")
        bias_min = spec[2] if spec else 175
        bias_max = spec[3] if spec else 225
        lines.append(f"<p style='color:red;font-weight:bold'>Bias alarm: one or more values out of {bias_min}–{bias_max}</p>")
        
    if master.get("fault") == 1 or slave.get("fault") == 1:
        lines.append("<p style='color:red;font-weight:bold'>Fault active: please investigate error code before proceeding.</p>")
        
    lines.append("<p>Diagnostics completed.</p>")
    return "".join(lines)

def render_performance_report(results):
    lines = []
    lines.append("<h3>Test de performance</h3>")
    
    if not results:
        lines.append("Aucun résultat de performance n'a été renvoyé par l'ATE.")
        return "".join(lines)

    categories = {
        "12007": "Input",
        "13101": "Bandwidth",
        "13102": "Bandwidth",
        "13103": "Power",
        "13104": "Power",
        "13105": "Power",
        "13106": "Gain",
        "13107": "Gain",
        "13108": "Stress",
        "13109": "Stress",
        "13110": "Stress",
        "13111": "Stress",
        "13112": "Stress",
        "13113": "Stress",
        "13114": "Stress",
        "13115": "Stress",
        "13201": "Harmonics",
        "13204": "Noise",
    }
    
    ok_count = sum(1 for r in results if r.status == "OK")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    total_count = len(results)
    
    overall_style = "color: green;" if fail_count == 0 else "color: red; font-weight: bold;"
    lines.append(f"<p style='{overall_style}'>Résumé: {ok_count} OK / {fail_count} FAIL / {total_count} Total</p>")
    
    grouped = {}
    for r in results:
        cat = categories.get(r.test_id, "Divers")
        grouped.setdefault(cat, []).append(r)
        
    for cat in sorted(grouped.keys()):
        lines.append(f"<h4>{cat}</h4>")
        lines.append(render_results_table(grouped[cat]))
        
    if fail_count > 0:
        lines.append("<p style='color:red;font-weight:bold'>Une ou plusieurs mesures de performance sont hors spécification.</p>")
        
    lines.append("<p>Test de performance terminé.</p>")
    return "".join(lines)
