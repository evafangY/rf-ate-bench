""" ATE instruments address """
scope_address = "TCPIP0::169.254.13.226::hislip0::INSTR"
vna_address = "TCPIP0::PC_ATE_RF_AMP::hislip_PXI10_CHASSIS1_SLOT1_INDEX0::INSTR"
en_address = "USB0::0x0957::0x2C07::MY62000370::0::INSTR"
rf_address = "USB0::0x0957::0x4807::MY59003502::0::INSTR"
comm_address = "ASRL5::INSTR"
master_address = "ASRL4::INSTR"
slave_address = "ASRL6::INSTR"

""" VNA configurations """
load_interpulse = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\inter_pulse.csa"'
load_gain_flatness = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\gain_flatness.csa"'
load_fidelity_forward = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\fidelity_forward.csa"'
load_fidelity_reverse = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\fidelity_reverse.csa"'
load_stress_1 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_1.csa"'
load_stress_2 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_2.csa"'
load_stress_3 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_3.csa"'
load_stress_4 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_4.csa"'
load_stress_5 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_5.csa"'
load_stress_6 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_6.csa"'
load_stress_7 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ATE_Lib_AN8103\vna_files\stress_7.csa"'
load_stress_8 = r'MMEM:LOAD:FILE "E:\rf-ate-bench\ate_lib_AN8103\vna_files\stress_8.csa"'

""" cables losses """
rf_loss = 0.0
scope_head_loss = 0.0
scope_body_loss = 0.0