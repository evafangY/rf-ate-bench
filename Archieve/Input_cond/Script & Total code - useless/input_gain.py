import pyvisa
import sys
import Libraries.input_gain_lib as input_gain_lib
import time
import math

# 1 connection to measurement devices
rm = pyvisa.ResourceManager()
rm_rs232 = pyvisa.ResourceManager('@py')

scope = rm.open_resource("USB0::0x0AAD::0x0197::1335.2050k04-101365::0::INSTR")
scope.timeout = 5000
print("scope:", scope.query("*IDN?"), end="")

swg33522B = rm.open_resource("USB0::0x0957::0x2C07::MY62000370::0::INSTR")
swg33522B.timeout = 5000
print("SWG for blanking:", swg33522B.query("*IDN?"), end="")

swg33611A = rm.open_resource("USB0::0x0957::0x4807::MY59003502::0::INSTR")
swg33611A.timeout = 5000
print("SWG for RF signal:", swg33611A.query("*IDN?"), end="")

srfd_com = rm_rs232.open_resource("ASRL5::INSTR")
srfd_com.baud_rate = 9600
srfd_com.data_bits = 8
srfd_com.stop_bits = pyvisa.constants.StopBits.one
srfd_com.parity = pyvisa.constants.Parity.none
srfd_com.timeout = 5000


# 2 Make sure the amplifier is in off state
input_gain_lib.poweroff(srfd_com)

# 3 configure mesurement devices 
input_gain_lib.config_scope(scope)
input_gain_lib.config_blanking_swg(swg33522B)

# 4 start the amplifier
input_gain_lib.standby(srfd_com)
input_gain_lib.body_mode(srfd_com)
input("change to body, then press enter")
input_gain_lib.operate(srfd_com)



# 5 verify the gain is not too high
input_gain_lib.config_rf_swg(swg33611A, "-20")
while True:
    scope.write("MEASurement1:RESult:ACTual?")
    output_power = 10 * math.log10(float(scope.read())**2/50)+90
    print("output power:", round(output_power, 1), "dBm, set the gain to have 50dBm")
    time.sleep(1)
    if (output_power >= 49.5) and (output_power <= 50.5):
        break
print("done")

# 6 measure the gain
input_gain_lib.config_rf_swg(swg33611A, "0")

while True:
    scope.write("MEASurement1:RESult:ACTual?")
    output_power = 10 * math.log10(float(scope.read())**2/50)+90
    print("output power:", round(output_power, 3), "dBm, set the gain to have 72dBm")
    time.sleep(1)
    if (output_power >= 71.9) and (output_power <= 72.1):
        break
print("done")

input_gain_lib.standby(srfd_com)



input_gain_lib.head_mode(srfd_com)
input("change to head, then press enter")
input_gain_lib.operate(srfd_com)

while True:
    scope.write("MEASurement1:RESult:ACTual?")
    output_power = 10 * math.log10(float(scope.read())**2/50)+90
    print("output power:", round(output_power, 3), "dBm, set the gain to have 63dBm")
    time.sleep(1)
    if (output_power >= 62.9) and (output_power <= 63.1):
        break
print("done")


# 7 stop the amplifier
input_gain_lib.off(swg33522B, swg33611A)
input_gain_lib.poweroff(srfd_com)