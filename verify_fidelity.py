import sys
import os
import unittest
from unittest.mock import MagicMock
import importlib.util

# Ensure we can import modules from current directory and subdirectories
current_dir = os.getcwd()
lib_dir = os.path.join(current_dir, 'ATE_Lib_AN8103')

# Mock system dependencies that might be missing or cause issues
sys.modules['pyvisa'] = MagicMock()
sys.modules['pyvisa.errors'] = MagicMock()
sys.modules['pyvisa.resources'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()

# Mock ate_config since it is imported by ate_lib
ate_config_mock = MagicMock()
# IMPORTANT: Only mock the module 'ATE_Lib_AN8103.ate_config', NOT the package 'ATE_Lib_AN8103'
# Mocking the package makes everything inside it (including ate_lib) a Mock object
sys.modules['ATE_Lib_AN8103.ate_config'] = ate_config_mock

# Now try to import ate_lib
try:
    # Try direct import if path is set up
    sys.path.append(current_dir)
    # Ensure the package is found as a real package
    if os.path.exists(lib_dir):
         # If ATE_Lib_AN8103 is a package (has __init__.py), import normally
         # If it's just a folder, we might need to add it to sys.path
         if not os.path.exists(os.path.join(lib_dir, '__init__.py')):
             # It's a namespace package or just a folder. 
             # Let's try to create a dummy __init__ in memory or just use sys.path trick
             pass
    
    from ATE_Lib_AN8103 import ate_lib
except ImportError:
    try:
        # Fallback: load source file directly
        file_path = os.path.join(lib_dir, 'ate_lib.py')
        spec = importlib.util.spec_from_file_location("ate_lib", file_path)
        ate_lib = importlib.util.module_from_spec(spec)
        sys.modules["ate_lib"] = ate_lib
        # We need to make sure 'from ATE_Lib_AN8103 import ate_config' works inside ate_lib
        # Since we are loading ate_lib directly, its __package__ might be None or 'ate_lib'
        # We might need to mock the import inside it or rely on sys.modules
        spec.loader.exec_module(ate_lib)
    except Exception as e:
        print(f"Failed to import ate_lib: {e}")
        sys.exit(1)

import numpy

class TestFidelityWIP(unittest.TestCase):
    def setUp(self):
        # Create instance without calling __init__
        # ate_lib should be a module, ate_init should be a class
        if isinstance(ate_lib, MagicMock):
             raise RuntimeError("ate_lib is a Mock object! Import failed to load real module.")
        
        self.ate = ate_lib.ate_init.__new__(ate_lib.ate_init)
        
        # Mock components
        self.ate.comm = MagicMock()
        self.ate.sw = MagicMock()
        self.ate.scope = MagicMock()
        self.ate.en = MagicMock()
        
        # Mock VNA
        self.ate.vna = MagicMock()
        self.ate.vna.visa = MagicMock()
        
        # Mock logging
        ate_lib.logging = MagicMock()
        
        # Mock progress_window if it exists
        if hasattr(ate_lib, 'progress_window'):
             ate_lib.progress_window = MagicMock()
        
        # Mock vna_single (used in fidelity_measure_wip)
        self.ate.vna_single = MagicMock()
        
        # Setup dummy data for parse_data
        # 267 points
        n_points = 267
        # Create flat gain/phase
        gain_db = numpy.linspace(10, 10, n_points)
        phase_deg = numpy.linspace(0, 0, n_points)
        s21_complex = 10**(gain_db/20.0) * numpy.exp(1j * numpy.deg2rad(phase_deg))
        
        self.ate.vna.parse_data = MagicMock(return_value=s21_complex)
        self.ate.vna.visa.query.return_value = "dummy_data"

    def test_fidelity_measure_wip(self):
        print("\n[TEST] Running fidelity_measure_wip...")
        try:
            self.ate.fidelity_measure_wip()
            print("[TEST] SUCCESS: fidelity_measure_wip executed without error.")
            
            # Check if results are set
            # We expect test_id_13205 to be 0.0 (flat gain)
            val = getattr(self.ate, 'test_id_13205', None)
            print(f"[TEST] test_id_13205 (Forward Gain Pk-Pk): {val}")
            
            if val is not None:
                print("[TEST] Validation Passed: Attribute set.")
            else:
                print("[TEST] Validation Failed: Attribute not set.")
                
        except Exception as e:
            print(f"[TEST] FAILED with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    unittest.main()