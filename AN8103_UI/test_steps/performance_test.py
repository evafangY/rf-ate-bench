
from ..phase_config import PHASE_CONFIG
from .test_result import TestResult
from ..phase_services import build_subtest_registry

def run_performance_sequence(ate, interaction_callback=None):
    """
    Executes all subtests defined for 'Performance test / burn' in sequence.
    Replaces the monolithic run_performance_test.
    """
    config = PHASE_CONFIG.get("Performance test / burn", {})
    subtests = config.get("subtests", [])
    registry = build_subtest_registry(ate, interaction_callback)
    
    all_results = []
    all_ok = True
    
    for sub in subtests:
        method_name = sub["method"]
        if method_name in registry:
            # Execute subtest
            res, ok = registry[method_name]()
            if isinstance(res, list):
                all_results.extend(res)
            else:
                # Should not happen given current implementation, but safety check
                pass
            
            if not ok:
                all_ok = False
        else:
            # Subtest not found in registry
            all_results.append(TestResult(
                test_id="ERROR",
                label=f"Subtest {method_name} implementation not found",
                value=0.0,
                unit="",
                min_spec=None,
                max_spec=None,
                status="FAIL"
            ))
            all_ok = False
            
    return all_results, all_ok
