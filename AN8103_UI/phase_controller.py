from .phase_services import (
    # Main phases
    run_diagnostic,
    run_output_conditional_simulation,
    run_power_module_gain_simulation,
    run_input_conditional_board_tuning,
    run_performance_test,
    run_configuration_finale,
    run_noise_blanked,
    # Sub phases registry
    build_subtest_registry,
    # Shared
    TestResult,
)
from .specs import PERFORMANCE_SPECS


def make_phase_runner(phase_name, ate, interaction_callback=None):
    def runner():
        result_phases = {
            "Power module gain tuning": lambda: run_power_module_gain_simulation(ate),
            "Input conditional board tuning": lambda: run_input_conditional_board_tuning(ate, interaction_callback),
            "Performance test / burn": lambda: run_performance_test(ate),
        }
        line_phases = {
            "Diagnostic": lambda: run_diagnostic(ate),
            "Output conditional tuning": lambda: run_output_conditional_simulation(ate),
            "Factory gain reset": lambda: run_configuration_finale(ate, interaction_callback),
            "Noise blanked": lambda: run_noise_blanked(ate),
        }
        if phase_name in result_phases:
            results, ok = result_phases[phase_name]()
            return results, ok
        if phase_name in line_phases:
            lines, ok, values = line_phases[phase_name]()
            return lines, ok, values
        return [f"{phase_name} is not implemented yet."], False, {}
    return runner


def make_subtest_runner(method_name, ate, interaction_callback=None):
    def runner():
        results = []
        ok = True
        registry = build_subtest_registry(ate, interaction_callback)
        if method_name in registry:
            return registry[method_name]()

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
                    
                    ok_value = True
                    if spec_min is not None and val < spec_min:
                        ok_value = False
                    if spec_max is not None and val > spec_max:
                        ok_value = False
                    status = "OK" if ok_value else "FAIL"
                    
                    results.append(TestResult(
                        test_id=test_id,
                        label=label,
                        value=val,
                        unit=unit,
                        min_spec=spec_min,
                        max_spec=spec_max,
                        status=status
                    ))
                    ok = ok_value
                else:
                    results.append(TestResult(
                        test_id="INFO",
                        label=f"Sous-test {method_name} terminé.",
                        value=0.0,
                        unit="",
                        min_spec=None,
                        max_spec=None,
                        status="INFO"
                    ))
            except Exception as e:
                ok = False
                results.append(TestResult(
                    test_id="ERROR",
                    label=f"Erreur pendant le sous-test {method_name}: {e}",
                    value=0.0,
                    unit="",
                    min_spec=None,
                    max_spec=None,
                    status="FAIL"
                ))
        else:
            ok = False
            results.append(TestResult(
                test_id="ERROR",
                label=f"Sous-test {method_name} indisponible sur cet ATE.",
                value=0.0,
                unit="",
                min_spec=None,
                max_spec=None,
                status="FAIL"
            ))
        return results, ok

    return runner
