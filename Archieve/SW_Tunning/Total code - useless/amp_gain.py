import pyvisa
import sys
import Libraries.amp_gain_lib as amp_gain_lib
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

srfd_amp_slave = rm_rs232.open_resource("ASRL3::INSTR")
srfd_amp_slave.baud_rate = 9600
srfd_amp_slave.data_bits = 8
srfd_amp_slave.stop_bits = pyvisa.constants.StopBits.one
srfd_amp_slave.parity = pyvisa.constants.Parity.none
srfd_amp_slave.timeout = 5000

srfd_amp_master = rm_rs232.open_resource("ASRL4::INSTR")
srfd_amp_master.baud_rate = 9600
srfd_amp_master.data_bits = 8
srfd_amp_master.stop_bits = pyvisa.constants.StopBits.one
srfd_amp_master.parity = pyvisa.constants.Parity.none
srfd_amp_master.timeout = 5000


# 2 Make sure the amplifier is in off state
# amp_gain_lib.poweroff(srfd_com)

# 3 configure mesurement devices 
amp_gain_lib.config_scope(scope)
amp_gain_lib.config_rf_swg(swg33611A)
amp_gain_lib.config_blanking_swg(swg33522B)

# 4 start the amplifier
amp_gain_lib.standby(srfd_com)

# 5 setting the gain (optionnal)
TARGET_DB = 69
TOLERANCE = 0.2   # marge d’erreur acceptable

def regulate_gain(srfd_amp, scope, meas_cmd):
    # Lire le gain actuel de l’ampli
    current_gain = int(amp_gain_lib.amp_check_gain(srfd_amp))
    print(f"Starting regulation from DAC={current_gain}")

    while True:
        # Mesure au scope
        scope.write(meas_cmd)
        measured = float(scope.read())
        db_value = 10 * math.log10(measured**2 / 50) + 90

        print(f"DAC={current_gain}, measured={db_value:.2f} dB")

        if abs(db_value - TARGET_DB) <= TOLERANCE:
            print(f"✅ Target reached: {db_value:.2f} dB")
            break

        # Ajustement automatique
        if db_value < TARGET_DB:
            current_gain += 1
        else:
            current_gain -= 1

        amp_gain_lib.amp_set_gain(srfd_amp, str(current_gain))
        time.sleep(0.5)

# Régulation master
amp_gain_lib.operate(srfd_com)
regulate_gain(srfd_amp_master, scope, "MEASurement1:RESult:ACTual?")

# Régulation slave
regulate_gain(srfd_amp_slave, scope, "MEASurement2:RESult:ACTual?")

amp_gain_lib.standby(srfd_com)
