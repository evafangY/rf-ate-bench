import time
import sys

def poweroff (srfd_com):
    state = -1
    print("setting the amp to off mode.", end="")
    sys.stdout.flush()
    srfd_com.write("MW3001 00\n")
    srfd_com.read()
    srfd_com.read()
    while (state != 0) or (wait == 1):
        state, wait = check_amp_state(srfd_com)
    print(" done")
    
def standby(srfd_com):
    state = -1
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

def amp_check_gain(srfd_amp):
    gain = srfd_write(srfd_amp, "DAC? 37\n")
    print("Amp gain:\t", gain)
    return gain

def amp_set_gain(srfd_amp, gain):
    srfd_write(srfd_amp, "PASS drowssap\n")
    print("Previous gain:\t", srfd_write(srfd_amp, "DAC? 37\n"))
    srfd_write(srfd_amp, f"DAC 37 {gain}\n")
    print("New gain:\t", srfd_write(srfd_amp, "DAC? 37\n"))
    print("saving gain")
    srfd_amp.write("EE:STOre:RF\n")
    time.sleep(0.1)
    srfd_amp.read()
    time.sleep(0.1)
    srfd_amp.read()
    time.sleep(0.1)
    print("Gain saved")

def srfd_write(srfd, command):
    srfd.write(command)
    srfd.read()
    return srfd.read().replace('\r', '').replace('>', '').replace('\n', '')

def check_amp_state (srfd_com):
    reg3011 = int(srfd_write(srfd_com, "MR3011\n"), 16)
    if (reg3011 & 0b10000000) == 128:
        print("fault occured, exiting")
        fault(srfd_com)
    state = (reg3011 & 0b00011000) >> 3
    wait = (reg3011 & 0b00000100) >> 2
    return state, wait

def fault (srfd_com):
    reg3011 = int(srfd_write(srfd_com, "MR3011\n"), 16)
    if (reg3011 & 0b10000000) == 128:
        reg3014 = srfd_write(srfd_com, "MR3014\n")
        print("fault:", reg3014)
        sys.exit()
    else:
        print("No faults occured")
        
def config_rf_swg(swg33611A):
    swg33611A.write("*RST")
    swg33611A.write("OUTPut1:LOAD 50")
    swg33611A.write("SOURce1:FUNCtion SIN")
    swg33611A.write("SOURCE1:FREQUENCY 63860000")
    swg33611A.write("SOURCE1:VOLT:UNIT DBM")
    swg33611A.write("SOURCE1:VOLT 0")
    swg33611A.write("OUTPUT1 ON")
    swg33611A.query("*OPC?")

def config_blanking_swg(swg33522B):
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
    
def config_scope(scope):
    scope.write("*RST")
    scope.write("CHANnel1:COUPling DC")
    scope.write("CHANnel2:COUPling DC")
    scope.write("TRIGger:MODE NORMal")
    scope.write("CHANnel1:BANDwidth 350E6")
    scope.write("CHANnel2:BANDwidth 350E6")
    scope.write("TRIGger:EVENt1:SOURce EXTernanalog")
    scope.write("TRIGger:ANEDge:LEVel 0.8")
    scope.write("TRIGger:ANEDge:COUPling DC")
    scope.write("TIMebase:SCALe 1E-8")
    scope.write("CHANnel1:SCALe 0.3")
    scope.write("CHANnel2:SCALe 0.3")
    scope.write("CHANnel1:STATe ON")
    scope.write("CHANnel2:STATe ON")
    scope.write("TIMebase:SCALe 1E-8")
    scope.write("TIMebase:HORizontal:POSition 0.0015")
    scope.write("MEASurement1:MAIN CYCRms")
    scope.write("MEASurement1:SOURce C1")
    scope.write("MEASurement2:MAIN CYCRms")
    scope.write("MEASurement2:SOURce C2")
    scope.query("*OPC?")
    
def off(swg33522B, swg33611A):
    swg33611A.write("OUTPUT1 OFF")
    swg33522B.write("OUTPUT1 OFF")
    swg33522B.write("OUTPUT2 OFF")


def shutdown_all(scope, swg33522B, swg33611A, srfd_com):
    try:
        swg33611A.write("OUTPUT1 OFF")
    except:
        pass

    try:
        swg33522B.write("OUTPUT1 OFF")
        swg33522B.write("OUTPUT2 OFF")
    except:
        pass

    try:
        scope.write("CHANnel1:STATe OFF")
    except:
        pass

    try:
        standby(srfd_com)
        poweroff(srfd_com)
    except:
        pass
