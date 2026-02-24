from .phase_services import (
    run_diagnostic,
    run_output_conditional_simulation,
    run_power_module_gain_simulation,
    run_input_conditional_simulation,
    run_performance_test,
    run_noise_blanked,
)
from .specs import PERFORMANCE_SPECS


def make_phase_runner(phase_name, ate):
    def runner():
        lines = []
        ok = True
        values = {}
        if phase_name == "Diagnostic":
            lines, ok, values = run_diagnostic(ate)
        elif phase_name in ("Output conditional tuning", "Tuning de la sortie conditionnelle"):
            lines, ok, values = run_output_conditional_simulation()
        elif phase_name in ("Power module gain tuning", "Tuning de la gain du module de puissance"):
            lines, ok, values = run_power_module_gain_simulation()
        elif phase_name in ("Input conditional board tuning", "Tuning de l'entrée conditionnelle"):
            lines, ok, values = run_input_conditional_simulation()
        elif phase_name in ("Performance test / burn", "Test de performance / burning"):
            lines, ok, values = run_performance_test(ate)
        elif phase_name in ("Noise blanked", "Mesure de bruit blanké"):
            lines, ok, values = run_noise_blanked(ate)
        else:
            lines.append(f"{phase_name} is not implemented yet.")
            ok = False
        return lines, ok, values

    return runner


def make_subtest_runner(method_name, ate):
    def runner():
        lines = []
        ok = True
        mapping = {
            "single_pulse_measure": ("13301", "test_id_13301"),
            "harmonic_output_measure": ("13201", "test_id_13201"),
            "noise_unblanked_measure": ("13204", "test_id_13204"),
        }
        if hasattr(ate, method_name):
            try:
                getattr(ate, method_name)()
                test_id, attr = mapping.get(method_name, (None, None))
                if test_id and attr and hasattr(ate, attr):
                    val = getattr(ate, attr)
                    spec = PERFORMANCE_SPECS.get(test_id)
                    label = method_name
                    unit = ""
                    spec_min = None
                    spec_max = None
                    if spec:
                        label = spec[0]
                        unit = spec[1]
                        spec_min = spec[2]
                        spec_max = spec[3]
                    status = ""
                    ok_value = True
                    if spec_min is not None and val < spec_min:
                        ok_value = False
                    if spec_max is not None and val > spec_max:
                        ok_value = False
                    status = "OK" if ok_value else "FAIL"
                    min_str = "" if spec_min is None else str(spec_min)
                    max_str = "" if spec_max is None else str(spec_max)
                    lines.append(
                        f"{test_id} – {label}: {round(val, 2)} {unit} "
                        f"[{min_str}..{max_str}] {status}"
                    )
                    ok = ok_value
                else:
                    lines.append(f"Sous-test {method_name} terminé.")
            except Exception as e:
                ok = False
                lines.append(f"Erreur pendant le sous-test {method_name}: {e}")
        else:
            ok = False
            lines.append(f"Sous-test {method_name} indisponible sur cet ATE.")
        return lines, ok

    return runner
