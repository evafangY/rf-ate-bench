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


def build_subtest_registry(ate, interaction_callback=None):
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
    }
