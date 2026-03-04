from .test_result import TestResult

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
