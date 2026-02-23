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

def body_mode(srfd_com):
    srfd_write(srfd_com, "MW3002 60\n")
    time.sleep(1)
    print("Amp set to body mode")

def head_mode(srfd_com):
    srfd_write(srfd_com, "MW3002 40\n")
    time.sleep(1)
    print("Amp set to head mode")

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
        
def config_rf_swg(swg33611A, dBm):
    swg33611A.write("*RST")
    swg33611A.write("OUTPut1:LOAD 50")
    swg33611A.write("SOURce1:FUNCtion SIN")
    swg33611A.write("SOURCE1:FREQUENCY 63860000")
    swg33611A.write("SOURCE1:VOLT:UNIT DBM")
    swg33611A.write(f"SOURCE1:VOLT {dBm}")
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
    scope.write("TRIGger:MODE NORMal")
    scope.write("CHANnel1:BANDwidth 350E6")
    scope.write("TRIGger:EVENt1:SOURce EXTernanalog")
    scope.write("TRIGger:ANEDge:LEVel 0.8")
    scope.write("TRIGger:ANEDge:COUPling DC")
    scope.write("TIMebase:SCALe 1E-8")
    scope.write("CHANnel1:SCALe 0.3")
    scope.write("CHANnel1:STATe ON")
    scope.write("TIMebase:SCALe 1E-8")
    scope.write("TIMebase:HORizontal:POSition 0.0015")
    scope.write("MEASurement1:MAIN CYCRms")
    scope.write("MEASurement1:SOURce C1")
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
        poweroff(srfd_com)
    except:
        pass
