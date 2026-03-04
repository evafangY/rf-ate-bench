from .test_steps.test_result import TestResult
from .test_steps.diagnostic_test import run_diagnostic
from .test_steps.output_conditional import run_output_conditional_simulation
from .test_steps.power_module_gain import run_power_module_gain_simulation
from .test_steps.input_tuning import (
    run_input_conditional_board_tuning,
    run_input_tuning_step_1,
    run_input_tuning_step_2,
    run_input_tuning_step_3,
    run_input_tuning_step_4,
    run_input_tuning_step_0dbm_body,
    run_input_tuning_step_0dbm_head,
)
from .test_steps.performance_test import run_performance_test
from .test_steps.factory_gain_tuning import (
    run_configuration_finale,
    run_factory_gain_pre_body,
    run_factory_gain_body_final,
    run_factory_gain_head_final,
)
from .test_steps.output_conditional_tuning import (
    run_step2_oscilloscope_tests,
    run_step2_resistance_head,
    run_step2_resistance_body,
)
from .test_steps.noise_test import run_noise_blanked
from .test_utils import create_test_result


def _run_measure_generic(ate, method_name, specs):
    """
    Generic runner for measurements.
    specs: list of (test_id, label, unit)
    """
    try:
        if hasattr(ate, method_name):
            getattr(ate, method_name)()
        else:
            return [TestResult("ERROR", f"Method {method_name} missing", 0, "", None, None, status="FAIL")], False

        results = []
        all_ok = True
        
        for test_id, label, unit in specs:
            attr = f"test_id_{test_id}"
            val = getattr(ate, attr, 0.0)
            res, ok = create_test_result(test_id, label, val, unit)
            results.append(res)
            if not ok: all_ok = False
            
        return results, all_ok
    except Exception as e:
        return [TestResult("ERROR", f"Error: {str(e)}", 0, "", None, None, status="FAIL")], False


def _run_stress_wrapper(ate, sequence, test_id_attr, label):
    try:
        ate.stress(sequence)
        val = getattr(ate, test_id_attr, 0.0)
        test_id = test_id_attr.replace("test_id_", "")
        res, ok = create_test_result(test_id, label, val, "%")
        return [res], ok
    except Exception as e:
        return [TestResult("ERROR", f"Error: {str(e)}", 0, "", None, None, status="FAIL")], False


def _run_stress_burst_wrapper(ate, sequence, test_id_attr, label):
    try:
        ate.stress_burst(sequence)
        val = getattr(ate, test_id_attr, 0.0)
        test_id = test_id_attr.replace("test_id_", "")
        res, ok = create_test_result(test_id, label, val, "%")
        return [res], ok
    except Exception as e:
        return [TestResult("ERROR", f"Error: {str(e)}", 0, "", None, None, status="FAIL")], False


def build_subtest_registry(ate, interaction_callback=None):
    # Specs for multi-value tests
    noise_blanked_specs = [
        ("13202", "Coherent noise blanked", "dBm/Hz"),
        ("13203", "Random noise blanked", "dBm/Hz")
    ]
    
    interpulse_specs = [
        ("13302", "Gain inter pulse stability", "dB"),
        ("13303", "Phase inter pulse stability", "deg")
    ]
    
    gain_flatness_specs = [
        ("12007", "RF input match", ":1"),
        ("13101", "Body gain flatness", "dB"),
        ("13102", "Head gain flatness", "dB"),
        ("13106", "Body gain", "dB"),
        ("13107", "Head gain", "dB")
    ]
    
    fidelity_specs = [
        ("13205", "Fidelity Forward Gain Pk-Pk", "dB"),
        ("13206", "Fidelity Forward dGain/dPin", "dB/dB"),
        ("13207", "Fidelity Forward dGain/dPin (Zone 2)", "dB/dB"),
        ("13208", "Fidelity Forward dGain/dPin (Zone 3)", "dB/dB"),
        ("13209", "Fidelity Forward Phase Pk-Pk", "deg"),
        ("13210", "Fidelity Forward dPhase/dPin", "deg/dB"),
        ("13211", "Fidelity Forward dPhase/dPin (Zone 2)", "deg/dB"),
        ("13212", "Fidelity Forward dPhase/dPin (Zone 3)", "deg/dB"),
        ("13213", "Fidelity Reverse Gain Pk-Pk", "dB"),
        ("13214", "Fidelity Reverse dGain/dPin", "dB/dB"),
        ("13215", "Fidelity Reverse dGain/dPin (Zone 2)", "dB/dB"),
        ("13216", "Fidelity Reverse dGain/dPin (Zone 3)", "dB/dB"),
        ("13217", "Fidelity Reverse Phase Pk-Pk", "deg"),
        ("13218", "Fidelity Reverse dPhase/dPin", "deg/dB"),
        ("13219", "Fidelity Reverse dPhase/dPin (Zone 2)", "deg/dB"),
        ("13220", "Fidelity Reverse dPhase/dPin (Zone 3)", "deg/dB"),
    ]

    return {
        "run_input_tuning_step_1": lambda: run_input_tuning_step_1(ate, interaction_callback),
        "run_input_tuning_step_2": lambda: run_input_tuning_step_2(ate, interaction_callback),
        "run_input_tuning_step_3": lambda: run_input_tuning_step_3(ate, interaction_callback),
        "run_input_tuning_step_4": lambda: run_input_tuning_step_4(ate, interaction_callback),
        "run_input_tuning_step_0dbm_body": lambda: run_input_tuning_step_0dbm_body(ate, interaction_callback),
        "run_input_tuning_step_0dbm_head": lambda: run_input_tuning_step_0dbm_head(ate, interaction_callback),
        "run_factory_gain_pre_body": lambda: run_factory_gain_pre_body(ate, interaction_callback),
        "run_factory_gain_body_final": lambda: run_factory_gain_body_final(ate, interaction_callback),
        "run_factory_gain_head_final": lambda: run_factory_gain_head_final(ate, interaction_callback),
        "run_step2_oscilloscope_tests": lambda: run_step2_oscilloscope_tests(ate, interaction_callback),
        "run_step2_resistance_head": lambda: run_step2_resistance_head(ate, interaction_callback),
        "run_step2_resistance_body": lambda: run_step2_resistance_body(ate, interaction_callback),
        
        # Performance tests - Unified Generic Runners
        "single_pulse_measure": lambda: _run_measure_generic(ate, "single_pulse_measure", [("13301", "Single pulse drop", "dB")]),
        "harmonic_output_measure": lambda: _run_measure_generic(ate, "harmonic_output_measure", [("13201", "Harmonic output", "dBc")]),
        "noise_unblanked_measure": lambda: _run_measure_generic(ate, "noise_unblanked_measure", [("13204", "Noise unblanked", "dBm/Hz")]),
        "noise_blanked_measure": lambda: _run_measure_generic(ate, "noise_blanked_measure", noise_blanked_specs),
        "interpulse_stability_measure": lambda: _run_measure_generic(ate, "interpulse_stability_measure", interpulse_specs),
        "gain_flatness_measure": lambda: _run_measure_generic(ate, "gain_flatness_measure", gain_flatness_specs),
        "fidelity_measure": lambda: _run_measure_generic(ate, "fidelity_measure", fidelity_specs),

        # Stress tests
        "run_stress_1": lambda: _run_stress_wrapper(ate, 1, "test_id_13108", "Stress 1"),
        "run_stress_2": lambda: _run_stress_wrapper(ate, 2, "test_id_13109", "Stress 2"),
        "run_stress_3": lambda: _run_stress_wrapper(ate, 3, "test_id_13110", "Stress 3"),
        "run_stress_4": lambda: _run_stress_wrapper(ate, 4, "test_id_13111", "Stress 4"),
        "run_stress_5": lambda: _run_stress_wrapper(ate, 5, "test_id_13112", "Stress 5"),
        "run_stress_6": lambda: _run_stress_burst_wrapper(ate, 6, "test_id_13113", "Stress Burst 6"),
        "run_stress_7": lambda: _run_stress_burst_wrapper(ate, 7, "test_id_13114", "Stress Burst 7"),
        "run_stress_8": lambda: _run_stress_burst_wrapper(ate, 8, "test_id_13115", "Stress Burst 8"),
    }
