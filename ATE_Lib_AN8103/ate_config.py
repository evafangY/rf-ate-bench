""" ATE instruments address """
scope_address = "TCPIP0::169.254.13.226::hislip0::INSTR"
vna_address = "TCPIP0::PC_ATE_RF_AMP::hislip_PXI10_CHASSIS1_SLOT1_INDEX0::INSTR"
en_address = "USB0::0x0957::0x2C07::MY62000370::0::INSTR"
rf_address = "USB0::0x0957::0x4807::MY59003502::0::INSTR"
sw_address = "USB0::0xF4EC::0x1900::SSUAAA0CA00003::0::INSTR"
comm_address = "ASRL5::INSTR"
master_address = "ASRL4::INSTR"
slave_address = "ASRL6::INSTR"

import os

# Base directory for VNA files
# Use the directory of the current script to locate vna_files dynamically
VNA_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vna_files")

""" VNA configurations """
load_interpulse = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\inter_pulse.csa"'
load_gain_flatness_body = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\gain_flatness_body.csa"'
load_gain_flatness_head = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\gain_flatness_head.csa"'
load_fidelity_forward = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\fidelity_forward.csa"'
load_fidelity_reverse = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\fidelity_reverse.csa"'
load_stress_1 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_1.csa"'
load_stress_2 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_2.csa"'
load_stress_3 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_3.csa"'
load_stress_4 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_4.csa"'
load_stress_5 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_5.csa"'
load_stress_6 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_6.csa"'
load_stress_7 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_7.csa"'
load_stress_8 = f'MMEM:LOAD:FILE "{VNA_FILES_DIR}\\stress_8.csa"'

""" cables losses """
rf_loss = 0.6
scope_head_loss = 60.97
scope_body_loss = 61.1