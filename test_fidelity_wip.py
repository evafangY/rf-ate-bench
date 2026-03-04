from ATE_Lib_AN8103.ate_lib import ate_init
import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run_fidelity_test():
    print("=== Fidelity Measure WIP Test Script ===")
    
    try:
        # 1. Initialize ATE
        print("\n[1/3] Initializing ATE instruments...")
        ate = ate_init()
        
        # 2. Run Fidelity Measure (New Implementation)
        print("\n[2/3] Running fidelity_measure()...")
        ate.fidelity_measure()
        
        # 3. Print Results
        print("\n[3/3] Test Results:")
        
        # List of test IDs related to fidelity measure
        # Based on ate_lib.py analysis
        fidelity_tests = [
            # Forward Gain Non-Linearity
            (13205, "Gain non-linearity, body forward (-40 to 0 dBm)", "dB"),
            # Forward Differential Gain
            (13206, "Differential gain, body forward (-40 to -3 dBm)", "dB/dB"),
            (13207, "Differential gain, body forward (-3 to -1 dBm)", "dB/dB"),
            (13208, "Differential gain, body forward (-1 to 0 dBm)", "dB/dB"),
            # Forward Phase Non-Linearity
            (13209, "Phase non-linearity, body forward (-40 to 0 dBm)", "deg"),
            # Forward Differential Phase
            (13210, "Differential phase, body forward (-40 to -3 dBm)", "deg/dB"),
            (13211, "Differential phase, body forward (-3 to -1 dBm)", "deg/dB"),
            (13212, "Differential phase, body forward (-1 to 0 dBm)", "deg/dB"),
            
            # Reverse Gain Non-Linearity
            (13213, "Gain non-linearity, body reverse (-40 to 0 dBm)", "dB"),
            # Reverse Differential Gain
            (13214, "Differential gain, body reverse (-40 to -3 dBm)", "dB/dB"),
            (13215, "Differential gain, body reverse (-3 to -1 dBm)", "dB/dB"),
            (13216, "Differential gain, body reverse (-1 to 0 dBm)", "dB/dB"),
            # Reverse Phase Non-Linearity
            (13217, "Phase non-linearity, body reverse (-40 to 0 dBm)", "deg"),
            # Reverse Differential Phase
            (13218, "Differential phase, body reverse (-40 to -3 dBm)", "deg/dB"),
            (13219, "Differential phase, body reverse (-3 to -1 dBm)", "deg/dB"),
            (13220, "Differential phase, body reverse (-1 to 0 dBm)", "deg/dB"),
        ]
        
        print(f"{'ID':<8} {'Description':<55} {'Value':<10} {'Unit':<5}")
        print("-" * 80)
        
        for test_id, desc, unit in fidelity_tests:
            attr_name = f"test_id_{test_id}"
            if hasattr(ate, attr_name):
                val = getattr(ate, attr_name)
                # Handle None or non-numeric gracefully
                if val is None:
                    val_str = "None"
                elif isinstance(val, (int, float)):
                    val_str = f"{val:.4f}"
                else:
                    val_str = str(val)
                print(f"{test_id:<8} {desc:<55} {val_str:<10} {unit:<5}")
            else:
                print(f"{test_id:<8} {desc:<55} {'MISSING':<10} {unit:<5}")
                
        print("\nDone.")
        
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_fidelity_test()