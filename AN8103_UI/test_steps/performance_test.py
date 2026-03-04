from AN8103_UI.specs import PERFORMANCE_SPECS
from .test_result import TestResult
from ..test_utils import create_test_result

def run_performance_test(ate):
    lines = []
    ok = True
    
    # Try to run the performance test on ATE, catching any crashes
    test_exception = None
    if hasattr(ate, "performance_test"):
        try:
            ate.performance_test()
        except Exception as e:
            test_exception = str(e)
            ok = False
            lines.append(f"Erreur critique pendant l'exécution du test de performance: {e}")
    else:
        lines.append("Fonction de test de performance non disponible dans AN8103_lib.")
        ok = False
        return lines, ok
    
    results = []
    def add_result(attr, test_id, label, unit):
        val = "MISSING"
        status_override = None

        if hasattr(ate, attr):
            val = getattr(ate, attr)
            if val is None:
                val = "N/A"
                status_override = "FAIL"
        else:
            status_override = "FAIL"

        # create_test_result will look up specs (label/unit/limits) automatically
        res, ok = create_test_result(test_id, label, val, unit)
        
        if status_override:
            res.status = status_override
            
        results.append(res)

    add_result("test_id_13301", "13301", "Single pulse drop", "dB")
    add_result("test_id_13302", "13302", "Gain inter pulse stability", "dB")
    add_result("test_id_13303", "13303", "Phase inter pulse stability", "deg")
    add_result("test_id_12007", "12007", "Input VSWR", ":1")
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
    add_result("test_id_13205", "13205", "Fidelity gain non linearity -40 to 0dBm", "dB")
    add_result("test_id_13206", "13206", "Fidelity differential gain -40 to -3dBm", "dB/dB")
    add_result("test_id_13207", "13207", "Fidelity differential gain -3 to -1dBm", "dB/dB")
    add_result("test_id_13208", "13208", "Fidelity differential gain -1 to 0dBm", "dB/dB")
    add_result("test_id_13209", "13209", "Fidelity phase non linearity -40 to 0dBm", "deg")
    add_result("test_id_13210", "13210", "Fidelity differential phase -40 to -3dBm", "deg/dB")
    add_result("test_id_13211", "13211", "Fidelity differential phase -3 to -1dBm", "deg/dB")
    add_result("test_id_13212", "13212", "Fidelity differential phase -1 to 0dBm", "deg/dB")
    add_result("test_id_13213", "13213", "Fidelity gain non linearity 0 to -40dBm", "dB")
    add_result("test_id_13214", "13214", "Fidelity differential gain -3 to -40dBm", "dB/dB")
    add_result("test_id_13215", "13215", "Fidelity differential gain -1 to -3dBm", "dB/dB")
    add_result("test_id_13216", "13216", "Fidelity differential gain 0 to -1dBm", "dB/dB")
    add_result("test_id_13217", "13217", "Fidelity phase non linearity 0 to -40dBm", "deg")
    add_result("test_id_13218", "13218", "Fidelity differential phase -3 to -40dBm", "deg/dB")
    add_result("test_id_13219", "13219", "Fidelity differential phase -1 to -3dBm", "deg/dB")
    add_result("test_id_13220", "13220", "Fidelity differential phase 0 to -1dBm", "deg/dB")
    
    if not results:
        ok = False
        lines.append("Aucun résultat de performance n'a été renvoyé par l'ATE.")
        # values = {}
        return lines, ok
    
    if test_exception:
        results.insert(0, TestResult(
            test_id="CRASH",
            label=f"Erreur critique: {test_exception}",
            value="ERROR",
            unit="",
            min_spec=None,
            max_spec=None,
            status="FAIL"
        ))

    # Check overall status
    if any(r.status == "FAIL" for r in results):
        ok = False

    return results, ok
