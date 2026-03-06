from .phase_services import (
    # Main phases
    run_diagnostic,
    run_output_conditional_simulation,
    run_power_module_gain_simulation,
    run_input_conditional_board_tuning,
    run_configuration_finale,
    run_noise_blanked,
    # Sub phases registry
    build_subtest_registry,
    # Shared
    TestResult,
)
from .test_steps.performance_test import run_performance_sequence


def make_phase_runner(phase_name, ate, interaction_callback=None):
    def runner():
        result_phases = {
            "Power module gain tuning": lambda: run_power_module_gain_simulation(ate),
            "Input conditional board tuning": lambda: run_input_conditional_board_tuning(ate, interaction_callback),
            "Performance test / burn": lambda: run_performance_sequence(ate, interaction_callback),
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

        # Fallback for methods not in registry but present on ATE
        if hasattr(ate, method_name):
            try:
                getattr(ate, method_name)()
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
