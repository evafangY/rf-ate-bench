import pyvisa
import time
import math
import numpy

from Libraries.srfd_lna_lib import (
    config_BL_swg,
    config_scope_spectrum,
    config_amp_channels,
    poweroff,
    standby,
    operate,
    power_off_system_33522B,
    config_lna_psu,
    check_amp_state,
    RBW_HZ
)

# ---------------------------------------------------------
# Limite de bruit unblanked
# ---------------------------------------------------------
LIMIT_UNBLANKED = -70  # dBm/Hz

# ---------------------------------------------------------
# SHUTDOWN FUNCTION - Emergency use only
# ---------------------------------------------------------
def shutdown(swg33522B, psu, srfd_com, reason):
    print(f"\nshutdown: {reason}")
    power_off_system_33522B(swg33522B, psu, srfd_com)
    check_amp_state(srfd_com)


# ---------------------------------------------------------
# INITIALISATION VISA
# ---------------------------------------------------------
def init_instruments():
    rm = pyvisa.ResourceManager()

    swg33522B = rm.open_resource("USB0::0x0957::0x2A07::MY59003503::0::INSTR")
    swg33522B.timeout = 5000

    scope = rm.open_resource("USB0::0x0AAD::0x0197::1335.2050k04-101598::0::INSTR")
    scope.timeout = 5000

    psu = rm.open_resource("ASRL5::INSTR") 
    rm_rs232 = pyvisa.ResourceManager('@py')
    srfd_com = config_amp_channels(rm_rs232)

    return swg33522B, scope, psu, srfd_com


# ---------------------------------------------------------
# CONFIGURATION COMPLETE DU BANC
# ---------------------------------------------------------
def setup_bench(psu, swg33522B, scope):
    config_lna_psu(psu)
    config_BL_swg(swg33522B)               # configure blanking/unblanking
    config_scope_spectrum(scope)    # scope en mode spectre
    time.sleep(1)                   # stabilisation


# ---------------------------------------------------------
# SEQUENCE COMPLETE AMPLI
# ---------------------------------------------------------
def setup_amplifier(srfd_com):
    poweroff(srfd_com)
    standby(srfd_com)
    operate(srfd_com)


# ---------------------------------------------------------
# MESURE BRUIT UNBLANKED
# ---------------------------------------------------------
def measure_noise(scope, srfd_com, psu, swg):
    scope.write("FORM ASC")
    scope.write("CALCulate:SPECtrum1:WAVeform:NORMal:DATA:VALues?")
    raw_fft = scope.read()
    data_fft = [float(val) for val in raw_fft.strip().split(',')]
    fft_array = numpy.array(data_fft)

    # moyenne du bruit mesuré au scope
    val_dBm = numpy.average(fft_array)

    # conversion en densité spectrale + correction LNA + coupleur
    val_dBmHz = val_dBm - 10 * math.log10(RBW_HZ) - 30 + 60

    if val_dBmHz > LIMIT_UNBLANKED:
        shutdown(srfd_com, psu, swg, "noise level approaching backend safety limit")

    return val_dBm, val_dBmHz


# ---------------------------------------------------------
# AFFICHAGE RESULTATS
# ---------------------------------------------------------
def print_results(val_dBm, val_dBmHz):
    print("\n--- UNBLANKED NOISE MEASUREMENT ---")
    print(f"bruit mesuré (dBm)    : {val_dBm:.2f}")
    print(f"bruit corrigé (dBm/Hz): {val_dBmHz:.2f}")
    print("\nunblanked PASS ?", val_dBmHz < LIMIT_UNBLANKED)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    swg33522B, scope, srfd_com, psu = init_instruments()
    setup_amplifier(srfd_com)
    setup_bench(swg33522B, scope)
    val_dBm, val_dBmHz = measure_noise(scope, srfd_com, swg33522B, psu)
    print_results(val_dBm, val_dBmHz)
    power_off_system_33522B(swg33522B, psu, srfd_com)


# ---------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
