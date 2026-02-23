import time
import pyvisa
import sys
import math

# constantes
F0_HZ = 63860000
RBW_HZ = 31.67
LNA_GAIN_DB = 28.0
LNA_NF_DB = 3.0

# -----------------------------------------
# CONFIG GENERATEUR RF (33611A)
# -----------------------------------------
def config_rf_swg(swg33611A, dBm):
    swg33611A.write("*RST")
    swg33611A.write("OUTPut1:LOAD 50")
    swg33611A.write("SOURce1:FUNC SIN")
    swg33611A.write("SOURce1:FREQ 63860000")
    swg33611A.write("SOURce1:VOLT:UNIT DBM")
    swg33611A.write("SOURce1:VOLT 0")
    swg33611A.write("OUTPut1 ON")
    swg33611A.query("*OPC?")

# -----------------------------------------
# CONFIG GENERATEUR Blanking / UnBlanking (33522B)
# -----------------------------------------
def config_BL_swg(swg33522B):
    swg33522B.write("*RST")
    swg33522B.write("SOURce1:TRACk INVerted")
    swg33522B.write("OUTPut1:LOAD INFinity")
    swg33522B.write("SOURce1:FUNCtion SQUare")
    swg33522B.write("SOURce1:VOLTage:LOW 0")
    swg33522B.write("SOURce1:VOLTage:HIGH 5")
    swg33522B.write("FUNCTION:SQUARE:PERIOD 1")
    swg33522B.write("SOURce1:FUNCtion:SQUare:DCYCle 0.3")
    swg33522B.write("OUTPUT1 ON")
    swg33522B.write("OUTPUT2 ON")
    swg33522B.query("*OPC?")

# -----------------------------------------
# CONFIG SCOPE EN MODE ANALYSEUR DE SPECTRE
# -----------------------------------------
def config_scope_spectrum(scope):
    scope.write("*RST")
    scope.write("CHANnel1:COUPling DC")
    scope.write("TRIGger:MODE NORMal")
    scope.write("TRIGger:EVENt1:SOURce EXTernanalog")
    scope.write("TRIGger:ANEDge:LEVel 0.8")
    scope.write("TRIGger:ANEDge:COUPling DC")
    scope.write("CHANnel1:SCALe 0.005")
    scope.write("TIMebase:SCALe 1E-2")
    scope.write("TIMebase:HORizontal:POSition 0.03")
    scope.write("ACQuire:SRAte:MODe MAN")
    scope.write("ACQuire:SRAte 5E9")
    scope.write("ACQuire:POINTs:MODE MANual")
    scope.write("ACQuire:POINTs:VALue 500E6")
    scope.write("TRIGger:MODE SINGLe")
    scope.write("CHANnel1:BANDwidth 1E8")
    scope.write("CALCulate:SPECtrum1:SOURce C1")
    scope.write("CALCulate:SPECtrum1:FREQuency:STARt 63.585E6")
    scope.write("CALCulate:SPECtrum1:FREQuency:STOP 64.135E6")
    scope.write("CALCulate:SPECtrum1:GATE:STARt 0")
    scope.write("CALCulate:SPECtrum1:GATE:Stop 0.06")
    scope.write("CALCulate:SPECtrum1:MAGNitude:LEVel -70")
    scope.write("CALCulate:SPECtrum1:STATe ON")
    scope.query("*OPC?")

# -----------------------------------------
# CONFIG ALIM LNA
# -----------------------------------------
def config_lna_psu(psu): 
    psu.write("VSET1:15")

def power_off_system_33611A(swg33611A, psu, srfd_com):
    psu.write("VSET1:0")
    swg33611A.write("OUTP OFF")
    poweroff(srfd_com)

def power_off_system_33522B(swg33522B, psu, srfd_com):
    psu.write("VSET1:0")
    swg33522B.write("OUTP OFF")
    poweroff(srfd_com)

# -----------------------------------------
# CONFIG PORTS SERIE AMPLI
# -----------------------------------------
def config_amp_channels(rm_rs232):
    srfd_com = rm_rs232.open_resource("ASRL6::INSTR")

    for dev in [srfd_com]:
        dev.baud_rate = 9600
        dev.data_bits = 8
        dev.stop_bits = pyvisa.constants.StopBits.one
        dev.parity = pyvisa.constants.Parity.none
        dev.timeout = 5000

    return srfd_com

# -----------------------------------------
# ETAT AMPLI
# -----------------------------------------
def check_amp_state(srfd_com):
    srfd_com.write("MR3011\n")
    srfd_com.read()
    ans = int(srfd_com.read(), 16)
    #print("ans:", ans)
    try:
        state = (ans & 0b00011000) >> 3
        wait = (ans & 0b00000100) >> 2
        #print(state, wait)
        return int(state), int(wait)
    except:
        return -1, 1

# -----------------------------------------
# MODE OFF
# -----------------------------------------
def poweroff(srfd_com):
    state, wait = -1, 1
    print("setting the amp to off mode.", end="")
    sys.stdout.flush()

    srfd_com.write("MW3001 00\n")
    srfd_com.read()
    srfd_com.read()

    while (state != 0) or (wait == 1):
        state, wait = check_amp_state(srfd_com)

    print(" done")

# -----------------------------------------
# MODE STANDBY
# -----------------------------------------
def standby(srfd_com):
    state, wait = -1, 1
    print("setting the amp to standby mode.", end="")
    sys.stdout.flush()

    srfd_com.write("MW3001 01\n")
    srfd_com.read()
    srfd_com.read()

    while (state != 1) or (wait == 1):
        state, wait = check_amp_state(srfd_com)
        time.sleep(0.5)
        print(".", end="")
        sys.stdout.flush()

    print(" done")

# -----------------------------------------
# MODE OPERATE
# -----------------------------------------
def operate(srfd_com):
    state, wait = check_amp_state(srfd_com)

    if state == 0:
        standby(srfd_com)

    print("setting the amp to operate mode.", end="")
    sys.stdout.flush()

    srfd_com.write("MW3001 03\n")
    srfd_com.read()
    srfd_com.read()

    while (state != 3) or (wait == 1):
        state, wait = check_amp_state(srfd_com)
        time.sleep(0.5)
        print(".", end="")
        sys.stdout.flush()

    print(" done")

def read_error_register(srfd_com):
    srfd_com.write("MR3014\n")
    srfd_com.read()
    value = srfd_com.read()
    return value.replace('\r', '').replace('\n', '').replace('>', '')

# -----------------------------------------
# RECONSTRUCTION BRUIT SANS LNA
# -----------------------------------------
def compute_noise_at_amp_input(noise_with_lna_dBmHz):
    return noise_with_lna_dBmHz - LNA_GAIN_DB
    #return noise_with_lna_dBmHz - LNA_GAIN_DB + LNA_NF_DB -> calcul theorique 


