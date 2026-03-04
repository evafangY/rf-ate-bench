from typing import Optional, Tuple, Any
from .test_steps.test_result import TestResult
from .specs import PERFORMANCE_SPECS, NOISE_SPECS, INPUT_COND_SPECS, OUTPUT_COND_SPECS, DIAGNOSTIC_SPECS


def check_spec(test_id: str, val: Any) -> Tuple[Optional[float], Optional[float], bool]:
    """
    Checks if a value meets the specification for a given test_id.
    Returns (min_val, max_val, is_ok).
    """
    spec = None
    if test_id in PERFORMANCE_SPECS:
        spec = PERFORMANCE_SPECS[test_id]
    elif test_id in NOISE_SPECS:
        spec = NOISE_SPECS[test_id]
    elif test_id in INPUT_COND_SPECS:
        spec = INPUT_COND_SPECS[test_id]
    elif test_id in OUTPUT_COND_SPECS:
        spec = OUTPUT_COND_SPECS[test_id]
    elif test_id in DIAGNOSTIC_SPECS:
        spec = DIAGNOSTIC_SPECS[test_id]
    
    if spec is None:
        return None, None, True
    
    # Spec tuple format: (description, unit, min_val, max_val)
    min_val = spec[2]
    max_val = spec[3]
    
    ok = True
    # Handle numeric checks only if val is numeric
    if isinstance(val, (int, float)):
        if min_val is not None and val < min_val:
            ok = False
        if max_val is not None and val > max_val:
            ok = False
    
    return min_val, max_val, ok


def create_test_result(test_id: str, label: str, val: Any, unit: str = "") -> Tuple[TestResult, bool]:
    """
    Creates a TestResult object and checks against specs.
    Returns (TestResult, is_ok).
    """
    spec_min, spec_max, ok = check_spec(test_id, val)
    
    # Try to fetch label/unit from specs if available to ensure consistency
    spec = None
    if test_id in PERFORMANCE_SPECS:
        spec = PERFORMANCE_SPECS[test_id]
    elif test_id in NOISE_SPECS:
        spec = NOISE_SPECS[test_id]
    elif test_id in INPUT_COND_SPECS:
        spec = INPUT_COND_SPECS[test_id]
    elif test_id in OUTPUT_COND_SPECS:
        spec = OUTPUT_COND_SPECS[test_id]
    elif test_id in DIAGNOSTIC_SPECS:
        spec = DIAGNOSTIC_SPECS[test_id]
        
    if spec:
        # spec is (label, unit, min, max)
        label = spec[0]
        unit = spec[1]
    
    status = "OK" if ok else "FAIL"
    return TestResult(test_id, label, val, unit, spec_min, spec_max, status=status), ok
