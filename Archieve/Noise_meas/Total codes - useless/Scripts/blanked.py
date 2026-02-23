import pyvisa
import time
import math
import numpy 

from Libraries.srfd_lna_lib import (
    config_rf_swg,
    config_scope_spectrum,
    config_lna_psu,
    config_amp_channels,
    poweroff,
    standby,
    operate,
    power_off_system_33611A,
    RBW_HZ
)


# ---------------------------------------------------------
# Constantes
# ---------------------------------------------------------
LIMIT_COHERENT = -143
LIMIT_RANDOM   = -160


# ---------------------------------------------------------
# SHUTDOWN FUNCTION - Emergency use only
# ---------------------------------------------------------

def shutdown(srfd_com, psu, swg33611A, reason):
    print(f"\nshutdown: {reason}")
    power_off_system_33611A(swg33611A, psu, srfd_com)

# ---------------------------------------------------------
# INITIALISATION VISA
# ---------------------------------------------------------
def init_instruments() :
    
    rm = pyvisa.ResourceManager()

    swg33611A   = rm.open_resource("USB0::0x0957::0x4807::MY59003502::0::INSTR")
    swg33611A.timeout = 5000

    scope = rm.open_resource("USB0::0x0AAD::0x0197::1335.2050k04-101598::0::INSTR")
    scope.timeout = 5000

    psu   = rm.open_resource("ASRL5::INSTR")
    psu.timeout = 5000

    rm_rs232 = pyvisa.ResourceManager('@py')
    srfd_com = config_amp_channels(rm_rs232)

    return swg33611A, scope, psu, srfd_com


# ---------------------------------------------------------
# CONFIGURATION COMPLETE DU BANC
# ---------------------------------------------------------
def setup_bench(swg33611A, scope, psu):
    config_lna_psu(psu)
    config_rf_swg(swg33611A, dBm=-20)
    config_scope_spectrum(scope)
    time.sleep(1)

# ---------------------------------------------------------
# SEQUENCE COMPLETE AMPLI
# ---------------------------------------------------------
def setup_amplifier(srfd_com):
    poweroff(srfd_com)
    standby(srfd_com)
    operate(srfd_com)
    
    
# ---------------------------------------------------------
# MESURE BRUIT
# ---------------------------------------------------------
def measure_noise(scope):
    #val_dBm = float(scope.query("CALC:MARK1:Y?"))

    scope.write("FORM ASC")
    scope.write("CALCulate:SPECtrum1:WAVeform:NORMal:DATA:VALues?")
    raw_fft = scope.read()
    data_fft = [float(val) for val in raw_fft.strip().split(',')]
    fft_data_array_harmonic = numpy.array(data_fft)

    random_noise = numpy.average(fft_data_array_harmonic) - 10 * math.log10(RBW_HZ) - 30

    coherent_noise = numpy.max(fft_data_array_harmonic)- 10 * math.log10(RBW_HZ) - 30

    return random_noise, coherent_noise


# ---------------------------------------------------------
# AFFICHAGE RESULTATS
# ---------------------------------------------------------
def print_results(random_noise, coherent_noise):
    print("\n--- BLANKED NOISE MEASUREMENT ---")
    print(f"bruit mesuré random (dBm/Hz)        : {random_noise:.2f}")
    print(f"bruit mesuré coherent (dBm/Hz)     : {coherent_noise:.2f}")
    #print(f"bruit entrée ampli (dBm/Hz): {bruit_amp:.2f}")

    print("\ncoherent noise PASS ?" , coherent_noise   < LIMIT_COHERENT)
    print("random noise PASS ?"   , random_noise < LIMIT_RANDOM)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    swg33611A, scope, psu, srfd_com = init_instruments()
    setup_amplifier(srfd_com)
    setup_bench(swg33611A, scope, psu)
    random_noise, coherent_noise = measure_noise(scope)
    print_results(random_noise, coherent_noise)
    power_off_system_33611A(swg33611A, psu, srfd_com)

# ---------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
