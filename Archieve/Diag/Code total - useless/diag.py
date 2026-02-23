import pyvisa
import sys
from srfd_lib import amp
import time

rm_rs232 = pyvisa.ResourceManager('@py')
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


amp.com_diag(srfd_com)

amp.poweroff(srfd_com)

amp.standby(srfd_com)


# amp.amp_set_gain(srfd_amp_master, 100)
# amp.amp_set_gain(srfd_amp_slave, 100)
# amp.amp_auto_bias(srfd_amp_master)
# amp.amp_auto_bias(srfd_amp_slave)


amp.com_diag(srfd_com)
print("Master amp:")
amp.amp_diag(srfd_amp_master)
print("Slave amp:")
amp.amp_diag(srfd_amp_slave)

amp.poweroff(srfd_com)

