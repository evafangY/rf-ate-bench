import time
import sys

def amp_poweroff (srfd_com):
    state = -1
    print("setting the amp to off mode.", end="")
    sys.stdout.flush()
    srfd_com.write("MW3001 00\n")
    srfd_com.read()
    srfd_com.read()
    while (state != 0) or (wait == 1):
        state, wait = check_amp_state(srfd_com)
    print(" done")
    
def amp_standby(srfd_com):
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

def amp_operate(srfd_com):
    state, wait = check_amp_state(srfd_com)
    if state == 0:
        amp_standby(srfd_com)
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

def com_diag(srfd_com):
    print()
    print("---- START OF COM DIAGNOSTIC ----")
    reg3011 = int(srfd_write(srfd_com, "MR3011\n"), 16)
    state = (reg3011 & 0b00011000) >> 3
    if state == 0:
        state_str = "power off"
    elif state == 1:
        state_str = "standby"
    elif state == 3:
        state_str = "operate"
    else:
        state_str = str(state)
    print("Amp state:\t\t", state_str)
    wait = (reg3011 & 0b00000100) >> 2
    print("Wait status:\t\t", wait)
    watchdog = "normal" if ((reg3011 & 0b00100000) >> 5) == 1 else "error occured"
    print("Whatchdog status:\t", watchdog)
    operate = "low power" if ((reg3011 & 0b01000000) >> 6) == 1 else "normal"
    print("Operate status:\t\t", operate)
    fault = "fault occured" if ((reg3011 & 0b10000000) >> 7) == 1 else "no faults"
    print("Fault status:\t\t", fault)
    reg3012 = int(srfd_write(srfd_com, "MR3012"), 16)
    mode = (reg3012 & 0b01100000) >> 5
    if mode == 1:
        mode_str = "test mode"
    elif mode == 2:
        mode_str = "head mode"
    elif mode == 3:
        mode_str = "body mode"
    else:
        mode_str = str(mode)
    print("Mode:\t\t\t", mode_str)
    print("Frequency code:\t\t", srfd_write(srfd_com, "MR3013\n"))
    print("Error code:\t\t", srfd_write(srfd_com, "MR3014\n"))
    print("----- END OF COM DIAGNOSTIC -----")
    print()
    
def body_mode(srfd_com):
    srfd_write(srfd_com, "MW3002 60\n")
    time.sleep(1)
    print("Amp set to body mode")

def head_mode(srfd_com):
    srfd_write(srfd_com, "MW3002 40\n")
    time.sleep(1)
    print("Amp set to head mode")

def test_mode(srfd_com):
    srfd_write(srfd_com, "MW3002 20\n")
    time.sleep(1)
    print("Amp set to test mode")
    
def srfd_write(srfd, command):
    srfd.write(command)
    srfd.read()
    return srfd.read().replace('\r', '').replace('>', '').replace('\n', '')
    
def amp_diag(srfd_amp):
    print()
    print("---- START OF AMP DIAGNOSTIC ----")    
    print("FAULT?:\t\t", srfd_write(srfd_amp, "FAULT?\n"))
    srfd_write(srfd_amp, "MEAS?\n")
    print("MEAS?:\t\t", srfd_amp.read().replace('\r', '').replace('>', '').replace('\n', ''))
    print("MODE?:\t\t", srfd_write(srfd_amp, "MODE?\n"))
    disp_amp_bias(srfd_amp)
    disp_amp_dac(srfd_amp)
    print("----- END OF AMP DIAGNOSTIC -----")
    print()

def amp_password (srfd_amp):
    srfd_write(srfd_amp, "PASS drowssap\n")
    
def amp_auto_bias (srfd_amp):
    amp_password (srfd_amp)
    print("registers before auto bias:")
    disp_amp_bias(srfd_amp)
    disp_amp_dac(srfd_amp)
    srfd_write(srfd_amp, "BIAS:AUTO\n")
    srfd_amp.read()
    print("processing autobias...")
    time.sleep(1)
    print("registers after auto bias:")
    disp_amp_bias(srfd_amp)
    disp_amp_dac(srfd_amp)
    print("saving bias...")
    srfd_write(srfd_amp, "EE:STO:RF\n")

def amp_set_gain(srfd_amp, gain):
    amp_password (srfd_amp)
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

def disp_amp_bias(srfd_amp):
    print("------------ biasing registers -------------")
    srfd_amp.write("BIAS:MEAS? 0\n")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    srfd_amp.read()

def disp_amp_dac(srfd_amp):
    amp_password (srfd_amp)
    print("-------------------------- DAC registers ---------------------------")
    srfd_amp.write("DAC? *\n")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    print(srfd_amp.read().replace('\r', ''), end="")
    print(srfd_amp.read().replace('\r', ''), end="")
    srfd_amp.read()
    
def amp_help(srfd_amp):
    amp_password (srfd_amp)
    print()
    print("---- BEGINING OF HELP COMMANDS ----")
    srfd_amp.write("HELP?\n")
    msg = srfd_amp.read()
    while msg != "\rPress a key\r\n":
        print(msg, end="")
        msg = srfd_amp.read() 
    srfd_amp.write("\n")
    msg = srfd_amp.read()
    while msg != "\rPress a key\r\n":
        print(msg, end="")
        msg = srfd_amp.read()
    srfd_amp.write("\n")
    msg = srfd_amp.read()
    while msg != "\r\n":
        print(msg, end="")
        msg = srfd_amp.read()
    print("---- END OF HELP COMMANDS ----")
    print()

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

def shutdown_all(srfd_com):
    try:
        amp_poweroff(srfd_com)
    except:
        pass
