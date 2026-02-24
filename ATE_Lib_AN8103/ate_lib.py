""" Dependencies """
import pyvisa
from pyvisa import constants
from pyvisa.errors import VisaIOError
import sys
import time
import numpy
import math
import csv
import tkinter
import tkinter.ttk
import tkinter.font
import logging
from ATE_Lib_AN8103 import ate_config

""" Amplifier error type definition """
class COMM_Error(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)

class ATE_Instrument_Error(Exception):
    def __init__(self, instrument_arg):
        self.instrument = instrument_arg
        super().__init__(instrument_arg)

""" ATE class definition """
class ate_init:
    def __init__(self):  
        try:
            logging.info("Starting ATE instruments initialization")
            self.scope = self.scope_init()
            self.vna = self.vna_init()
            self.en = self.en_init()
            self.rf = self.rf_init()
            self.sw = self.sw_init()
            self.comm = self.comm_init()
            self.master = self.amp_init("master")
            self.slave = self.amp_init("slave")
        except Exception:
            logging.warning("Exception occured during ATE instruments initialization")
            raise
    
    def emergency_stop (self):
        if tkinter._default_root is None:
            root = tkinter.Tk()
        else:
            root = tkinter.Toplevel(tkinter._default_root)
        root.title("Emergency stop result")
        root.geometry("370x170+530+200")
        logging.warning("Starting emergency stop")
        try:
            self.rf.poweroff()
            rfoff = tkinter.Label(root, text="RF generator off", anchor="w", fg="green")
        except Exception:
            logging.error("Unable to turn off the RF waveform generator")
            rfoff = tkinter.Label(root, text="RF GENERATOR MAY BE STILL ON!!!", anchor="w", fg="red")
        rfoff.pack(pady=(8, 0), padx=(32,0),  fill="x")
        try:
            self.en.poweroff()
            enoff = tkinter.Label(root, text="Unblanking generator off", anchor="w", fg="green")
        except Exception:
            logging.error("Unable to turn off the blanking waveform generator")
            enoff = tkinter.Label(root, text="UNBLANKING GENERATOR MAY BE STILL ON!!!", anchor="w", fg="red")
        enoff.pack(pady=(0, 0), padx=(32,0),  fill="x")
        try:
            self.vna.poweroff()
            vnaoff = tkinter.Label(root, text="Network analyzer off", anchor="w", fg="green")
        except Exception:
            logging.error("Unable to turn off the VNA")
            vnaoff = tkinter.Label(root, text="NETWORK ANALYZER MAY BE STILL ON!!!", anchor="w", fg="red")
        vnaoff.pack(pady=(0, 0), padx=(32,0),  fill="x")
        try:
            self.comm.poweroff()
            commoff = tkinter.Label(root, text="RF amplifier off", anchor="w", fg="green")
        except COMM_Error as comm_e:
            commoff = tkinter.Label(root, text=f"RF amplifier error {hex(comm_e.code)}", anchor="w", fg="orange")
        except Exception:
            logging.error("Unable to turn off the RF amplifier")
            commoff = tkinter.Label(root, text="RF AMPLIFIER MAY BE STILL ON!!!", anchor="w", fg="red")
        commoff.pack(pady=(0, 0), padx=(32,0),  fill="x")
        lbl2 = tkinter.Label(root, text="Please turn OFF manually the devices that may be still ON", anchor="w")
        lbl2.pack(pady=(8, 0), padx=(32,0),  fill="x")
        def btnclose():
            root.destroy()
        btn = tkinter.ttk.Button(root, text="OK", command=btnclose)
        btn.pack(pady=(8, 0))
        root.update_idletasks()
        root.wait_window()
    
    def poweroff (self):
        try:
            self.rf.poweroff()
            self.en.poweroff()
            self.vna.poweroff()
            self.comm.poweroff()
        except Exception:
            logging.warning("Exception occured during the ATE turn off")
            self.emergency_stop();
            raise
    
    """ Global tests definitions """
    def diagnostics(self):
        try:
            self.force_update()
            self.comm.standby()
            self.force_update()
            self.comm.poweroff()
        except COMM_Error as comm_e:
            logging.warning("Error %s occured during diagnostics", hex(comm_e.code))
        except Exception:
            logging.warning("Exception occured during diagnostics")
            self.emergency_stop();
            raise
        
    def force_update(self):
        try:
            self.comm.update()
        except COMM_Error as comm_e:
            logging.warning("Error %s occured during amp update", hex(comm_e.code))
        self.master.update_mode()
        self.master.update_fault()
        self.master.update_meas()
        self.slave.update_mode()
        self.slave.update_fault()
        self.slave.update_meas()
        if self.comm.state != 0:
            self.master.bias()
            self.master.dac()
            self.slave.bias()
            self.slave.dac()
    
    def performance_test (self):
        gui = progress_window("Performance test status", 1420,10,10); logging.info("starting performance test")
        # gui.set_status("Performing single pulse measure...", 1); self.single_pulse_measure()
        # gui.set_status("Performing harmonic output measure...", 33); self.harmonic_output_measure()
        # gui.set_status("Performing noise ublanked measure...", 67); self.noise_unblanked_measure()
        # gui.set_status("Interpulse stability measure", 1); self.interpulse_stability_measure()
        # gui.set_status("Gain flatness measure", 10); self.gain_flatness_measure()
        # gui.set_status("Stress sequence 5", 20); self.stress(5)
        # gui.set_status("Stress sequence 4", 30); self.stress(4)
        # gui.set_status("Stress sequence 3", 40); self.stress(3)
        # gui.set_status("Stress sequence 2", 50); self.stress(2)
        # gui.set_status("Stress sequence 1", 60); self.stress(1)
        # gui.set_status("Stress sequence 6", 70); self.stress_burst(6)
        # gui.set_status("Stress sequence 7", 80); self.stress_burst(7)
        # gui.set_status("Stress sequence 8", 90); self.stress_burst(8)
        gui.set_status("Fidelity measure", 90); self.fidelity_measure()
        gui.set_status("Performance test completed", 100); time.sleep(1)
        self.poweroff()
        gui.close()
    
    """ Tests definitions """
    def single_pulse_measure (self):
        try:
            gui = progress_window("Single pulse measure status"); logging.info("Starting single pulse measure")
            gui.set_status("Setting the amplifier in standy", 10); self.comm.standby()
            gui.set_status("Setting the switches", 1); self.sw.config("scope_body")
            gui.set_status("Setting the scope", 3); self.scope.config("single_pulse_measure")
            gui.set_status("Setting the unblanking generator", 6); self.en.config("1", "0.8")
            gui.set_status("Setting the RF generator", 9); self.rf.config("0")
            gui.set_status("Setting the amplifier in body mode", 11); self.comm.body()
            gui.set_status("Setting the amplifier in operate", 12); self.comm.operate()
            gui.set_status("Turning on input signals", 15); self.rf.operate(); self.en.operate()
            gui.set_status("Triggering the scope", 30); self.scope.single_trigger()
            gui.set_status("Setting the amplifier back to standby", 32); self.comm.standby()
            gui.set_status("Turning off the RF generator", 34); self.rf.poweroff()
            gui.set_status("Turning off the unblanking generator", 38); self.en.poweroff()
            gui.set_status("Setting single pulse measure...", 40); logging.info("Scope is calculating the cycle RMS...")
            self.scope.visa.write("MEASurement1:ENABLe ON")
            self.scope.visa.write("MEASurement1:MAIN CYCRms")
            self.scope.visa.write("MEASurement1:SOURCe C1")
            self.scope.visa.write("MEASurement1:TRACk:STATe ON")
            gui.set_status("Waiting for the scope to calculate single pulse measure...", 42); self.scope.visa.query("*OPC?")
            gui.set_status("Acquiring data from the scope...", 60); logging.info("Acquiring data from the scope...")
            self.scope.visa.write("FORMat:DATA REAL,64")
            self.scope.visa.write("MEASurement1:TRACk:DATA:VALues? 10000000,30000000")
            raw_data = self.scope.visa_binary(self.scope.visa.read_raw())
            gui.set_status("Processing scope data", 98); logging.info("Scope data acquired")
            min_rms = numpy.min(raw_data)
            max_rms = numpy.max(raw_data)
            self.test_id_13301 = 20 * math.log10(max_rms / min_rms)
            logging.info("Single pulse drop (13301):%s dB", round(self.test_id_13301, 2))
            logging.info("power during single pulse drop: %s dBm", round(10 * math.log10(numpy.mean(raw_data)**2/50)+60+30, 2))
            gui.set_status("Single pulse measure completed", 100); time.sleep(0.5)
            gui.close()
            logging.info("Single pulse measure completed")
        except Exception:
            gui.set_status("Error occured, turning off the ATE", 0); logging.warning("Exception while performing single pulse measure")
            self.emergency_stop();
            gui.close()
            raise
            
    def harmonic_output_measure (self):
        try:
            gui = progress_window("Harmonic output measure status"); logging.info("Harmonic output measure")
            gui.set_status("Setting the amplifier in standy", 16); self.comm.standby()
            gui.set_status("Setting the switches", 1); self.sw.config("scope_body")
            gui.set_status("Setting the scope", 5); self.scope.config("harmonic_output_measure")
            gui.set_status("Setting the unblanking generator", 10); self.en.config("1", "0.8")
            gui.set_status("Setting the RF generator", 15); self.rf.config("0")
            gui.set_status("Setting the amplifier in body mode", 19); self.comm.body()
            gui.set_status("Setting the amplifier in operate", 20); self.comm.operate()
            gui.set_status("Turning on input signals", 25); self.rf.operate(); self.en.operate()
            gui.set_status("Triggering the scope...", 30); self.scope.single_trigger()
            gui.set_status("Setting the amplifier back to standby", 40); self.comm.standby()
            gui.set_status("Turning off the RF generator", 45); self.rf.poweroff()
            gui.set_status("Turning off the unblanking generator", 50); self.en.poweroff()
            gui.set_status("Acquiring data from the scope...", 55); logging.info("Acquiring data from the scope...")
            self.scope.visa.write("FORM ASC")
            self.scope.visa.write("CALCulate:SPECtrum1:WAVeform:NORMal:DATA:VALues?")
            raw_fft = self.scope.visa.read()
            gui.set_status("Processing scope data", 95); print("Scope data acquired")
            data_fft = [float(val) for val in raw_fft.strip().split(',')]
            fft_data_array_harmonic = numpy.array(data_fft)
            cut = int(0.2*fft_data_array_harmonic.size)
            fondamental_array = fft_data_array_harmonic[:cut]
            harmoniques_array = fft_data_array_harmonic[cut:]
            fondamental = numpy.max(fondamental_array)
            harmonique = numpy.max(harmoniques_array)
            self.test_id_13201 = abs(fondamental - harmonique)
            logging.info("Harmonic output (13201): %s dB", round(self.test_id_13201, 2))
            gui.set_status("Harmonic output measure completed", 100); time.sleep(0.5)
            gui.close()
            logging.info("Harmonic output measure completed")
        except Exception:
            gui.set_status("Error occured, turning off the ATE", 0); logging.warning("Exception while performing harmonic output measure")
            self.emergency_stop();
            gui.close()
            raise
    
    def noise_unblanked_measure (self):
        try:
            gui = progress_window("Unblanked noise measure status"); logging.info("Starting unblanked noise measure")
            gui.set_status("Setting the amplifier in standy", 32); self.comm.standby()
            gui.set_status("Setting the switches", 10); self.sw.config("scope_body")
            gui.set_status("Making sure that the RF generator is OFF", 1); self.rf.poweroff()
            gui.set_status("Setting the scope", 20); self.scope.config("noise_unblanked_measure")
            gui.set_status("Setting the unblanking generator", 30); self.en.config("1", "2")
            gui.set_status("Setting the amplifier in body mode", 39); self.comm.body()
            gui.set_status("Setting the amplifier in operate", 40); self.comm.operate()
            gui.set_status("Turning on blanking signals", 9); self.en.operate()
            gui.set_status("Triggering the scope...", 50); self.scope.single_trigger()
            gui.set_status("Setting the amplifier back to standby", 60); self.comm.standby()
            gui.set_status("Turning off the unblanking generator", 70); self.en.poweroff()
            gui.set_status("Acquiring data from the scope...", 80); logging.info("Acquiring data from the scope...")
            self.scope.visa.write("FORM ASC")
            self.scope.visa.write("CALCulate:SPECtrum1:WAVeform:NORMal:DATA:VALues?")
            raw_fft = self.scope.visa.read()
            gui.set_status("Processing scope data", 90); logging.info("Scope data acquired")
            data_fft = [float(val) for val in raw_fft.strip().split(',')]
            fft_data_array_harmonic = numpy.array(data_fft)
            self.test_id_13204 = numpy.mean(fft_data_array_harmonic)-21.76+60 # a 60 dB coupler is used, subtract LNA gain, -21.76dB to nomalize to dBm/1Hz
            logging.info("Noise unblanked (13204): %s dBm/Hz", round(self.test_id_13204, 2))
            gui.set_status("Unblanked noise measure completed", 100); time.sleep(0.5)
            gui.close()
            logging.info("Unblanked noise measure completed")
        except Exception:
            gui.set_status("Error occured, turning off the ATE", 0); logging.warning("Error while performing noise unblanked measure")
            self.emergency_stop();
            gui.close()
            raise
            
    def interpulse_stability_measure (self):
        try:
            gui = progress_window("Interpulse stability measure status"); logging.info("Starting interpulse stability measure")
            gui.set_status("Setting the amplifier in standby", 10); self.comm.standby()
            gui.set_status("Making sure that the RF generator is OFF", 6); self.rf.poweroff()
            gui.set_status("Setting the switches", 2); self.sw.config("vna_body")
            gui.set_status("Setting the scope", 4); self.scope.config("")
            gui.set_status("Setting the unblanking generator", 8); self.en.config("0.125", "3.52")
            gui.set_status("Loading VNA configuration", 6); self.vna.visa.write(ate_config.load_interpulse)
            gui.set_status("Setting the amplifier in body mode", 11); self.comm.body()
            gui.set_status("Setting the amplifier in operate", 10); self.comm.operate()
            gui.set_status("Turning on blanking signals", 9); self.en.operate()
            gui.set_status("Waiting for VNA to acquire data... (please wait 1 minute)", 10); self.vna_single()
            gui.set_status("Setting the amplifier back to standby", 14); self.comm.standby()
            gui.set_status("Turning off the unblanking generator", 18); self.en.poweroff()
            gui.set_status("Acquiring data from the VNA", 10); s21_raw = self.vna.visa.query("CALC:MEAS1:DATA:FDATa?")
            gui.set_status("Processing VNA data", 98); logging.info("VNA data acquired")
            self.interpulse_s21_mag = 20 * numpy.log10(numpy.abs(self.vna.parse_data(s21_raw)))
            self.interpulse_s21_phase = numpy.degrees(numpy.angle(self.vna.parse_data(s21_raw)))
            self.test_id_13302 = numpy.max(self.interpulse_s21_mag) - numpy.min(self.interpulse_s21_mag)
            self.test_id_13303 = numpy.max(self.interpulse_s21_phase) - numpy.min(self.interpulse_s21_phase)
            logging.info("Gain inter pulse stability (13302): %sdB", round(self.test_id_13302, 2)) 
            logging.info("Phase inter pulse stability (13303): %s°", round(self.test_id_13303, 2))            
            gui.set_status("Interpulse stability measure completed", 100); time.sleep(0.5)
            gui.close()
            logging.info("Interpulse stability measure completed")
        except Exception:
            gui.set_status("Error occured during stability measure, turning off the ATE", 0); logging.warning("Error while performing interpulse stability measure")
            self.emergency_stop();
            gui.close()
            raise
            
    def gain_flatness_measure(self):
        try:
            gui = progress_window("Gain flatness measure status"); logging.info("Starting gain flatness measure")
            gui.set_status("Setting the amplifier in standby", 10); self.comm.standby()
            gui.set_status("Setting the switches", 2); self.sw.config("vna_body")
            gui.set_status("Setting the scope", 4); self.scope.config("")
            gui.set_status("Setting the unblanking generator", 8); self.en.config("0.125", "3.52")
            gui.set_status("Loading VNA configuration", 6); self.vna.visa.write(ate_config.load_gain_flatness)
            gui.set_status("Setting the amplifier in body mode", 11); self.comm.body()
            gui.set_status("Setting the amplifier in operate", 10); self.comm.operate()
            gui.set_status("Turning on blanking signals", 9); self.en.operate()
            gui.set_status("Waiting for VNA to acquire data... (please wait 1 minute)", 10); self.vna_single()
            gui.set_status("Setting the amplifier back to standby", 14); self.comm.standby()
            gui.set_status("Acquiring VNA data", 10)
            s11_raw = self.vna.visa.query("CALC:MEAS1:DATA:FDATa?")
            s21_raw = self.vna.visa.query("CALC:MEAS2:DATA:FDATa?")  
            gui.set_status("Setting the switches", 2); self.sw.config("vna_head")
            # gui.set_status("Setting the amplifier in head mode", 11); self.comm.head()
            gui.set_status("Setting the amplifier in operate", 10); self.comm.operate()
            gui.set_status("Waiting for VNA to acquire data... (please wait 1 minute)", 10); self.vna_single()
            gui.set_status("Setting the amplifier back to standby", 14); self.comm.standby()
            gui.set_status("Acquiring VNA data", 10); s21_raw_head = self.vna.visa.query("CALC:MEAS2:DATA:FDATa?")
            gui.set_status("Turning off the unblanking generator", 18); self.en.poweroff()
            s11 = numpy.abs(self.vna.parse_data(s11_raw))
            self.flatness_s11_mag = 20 * numpy.log10(s11)
            s11_max = numpy.max(s11)
            self.test_id_12007 = (1 + s11_max) / (1 - s11_max)
            self.flatness_s21_mag_body = 20 * numpy.log10(numpy.abs(self.vna.parse_data(s21_raw)))
            self.flatness_s21_mag_head = 20 * numpy.log10(numpy.abs(self.vna.parse_data(s21_raw_head)))
            self.test_id_13101 = numpy.max(self.flatness_s21_mag_body) - numpy.min(self.flatness_s21_mag_body)
            self.test_id_13102 = numpy.max(self.flatness_s21_mag_head) - numpy.min(self.flatness_s21_mag_head)
            self.test_id_13106 = numpy.mean(self.flatness_s21_mag_body)
            self.test_id_13107 = numpy.mean(self.flatness_s21_mag_head)
            logging.info("RF input match (12007): %s:1", round(self.test_id_12007, 2)) 
            logging.info("Body gain flatness (13101): %s dB", round(self.test_id_13101, 2))
            logging.info("Head gain flatness (13102): %s dB", round(self.test_id_13102, 2))
            logging.info("Body power (13106): %sdBm", round(self.test_id_13106, 2))
            logging.info("Head power (13107): %sdBm", round(self.test_id_13107, 2))
            gui.set_status("Gain flatness measure completed", 100); time.sleep(0.5)
            gui.close()
            logging.info("Gain flatness measure completed")
        except Exception:
            gui.set_status("Error occured during gain flatness measure, turning off the ATE", 0); logging.warning("Error while performing gain flatness measure")
            self.emergency_stop();
            gui.close()
            raise

    def fidelity_measure(self):
        try:
            gui = progress_window("Fidelity measure status"); logging.info("Starting fidelity measure")
            gui.set_status("Setting the amplifier in standby", 10); self.comm.standby()
            gui.set_status("Setting the switches", 2); self.sw.config("vna_body")
            gui.set_status("Setting the scope", 4); self.scope.config("")
            gui.set_status("Setting the unblanking generator", 8); self.en.config("0.2", "4.5")
            gui.set_status("Loading VNA configuration", 6); self.vna.visa.write(ate_config.load_fidelity_forward)
            gui.set_status("Setting the amplifier in body mode", 11); self.comm.body()
            gui.set_status("Setting the amplifier in operate", 10); self.comm.operate()
            gui.set_status("Turning on blanking signals", 9); self.en.operate()
            gui.set_status("Waiting for VNA to acquire data... (please wait 1 minute)", 10); self.vna_single()
            gui.set_status("Acquiring VNA data", 10); s21_raw = self.vna.visa.query("CALC:MEAS1:DATA:FDATa?")  
            self.forward_s21_mag = 20 * numpy.log10(numpy.abs(self.vna.parse_data(s21_raw)))
            self.forward_s21_mag_diff = numpy.gradient(self.forward_s21_mag, 0.15)
            self.forward_s21_phase = numpy.degrees(numpy.angle(self.vna.parse_data(s21_raw)))
            self.forward_s21_phase_diff = numpy.gradient(self.forward_s21_phase, 0.15)
            self.test_id_13205 = numpy.max(self.forward_s21_mag[133:]) - numpy.min(self.forward_s21_mag[133:])
            self.test_id_13206 = numpy.max(self.forward_s21_mag_diff[133:380]) - numpy.min(self.forward_s21_mag_diff[133:380])
            self.test_id_13207 = numpy.max(self.forward_s21_mag_diff[380:393]) - numpy.min(self.forward_s21_mag_diff[380:393])
            self.test_id_13208 = numpy.max(self.forward_s21_mag_diff[393:]) - numpy.min(self.forward_s21_mag_diff[393:])
            self.test_id_13209 = numpy.max(self.forward_s21_phase[133:]) - numpy.min(self.forward_s21_phase[133:])
            self.test_id_13210 = numpy.max(self.forward_s21_phase_diff[133:380]) - numpy.min(self.forward_s21_phase_diff[133:380])
            self.test_id_13211 = numpy.max(self.forward_s21_phase_diff[380:393]) - numpy.min(self.forward_s21_phase_diff[380:393])
            self.test_id_13212 = numpy.max(self.forward_s21_phase_diff[393:]) - numpy.min(self.forward_s21_phase_diff[393:])
            gui.set_status("Loading VNA configuration", 6); self.vna.visa.write(ate_config.load_fidelity_reverse)
            gui.set_status("Waiting for VNA to acquire data... (please wait 1 minute)", 10); self.vna_single()
            gui.set_status("Setting the amplifier back to standby", 14); self.comm.standby()
            gui.set_status("Turning off the unblanking generator", 18); self.en.poweroff()
            gui.set_status("Acquiring VNA data", 10); s21_raw = self.vna.visa.query("CALC:MEAS1:DATA:FDATa?")  
            self.reverse_s21_mag = 20 * numpy.log10(numpy.abs(self.vna.parse_data(s21_raw)))
            self.reverse_s21_mag_diff = numpy.gradient(self.reverse_s21_mag, 0.15)
            self.reverse_s21_phase = numpy.degrees(numpy.angle(self.vna.parse_data(s21_raw)))
            self.reverse_s21_phase_diff = numpy.gradient(self.reverse_s21_phase, 0.15)
            self.test_id_13213 = numpy.max(self.reverse_s21_mag[:267]) - numpy.min(self.reverse_s21_mag[:267])
            self.test_id_13214 = numpy.max(self.reverse_s21_mag_diff[20:267]) - numpy.min(self.reverse_s21_mag_diff[20:267])
            self.test_id_13215 = numpy.max(self.reverse_s21_mag_diff[7:20]) - numpy.min(self.reverse_s21_mag_diff[7:20])
            self.test_id_13216 = numpy.max(self.reverse_s21_mag_diff[:7]) - numpy.min(self.reverse_s21_mag_diff[:7])
            self.test_id_13217 = numpy.max(self.reverse_s21_phase[:267]) - numpy.min(self.reverse_s21_phase[:267])
            self.test_id_13218 = numpy.max(self.reverse_s21_phase_diff[20:267]) - numpy.min(self.reverse_s21_phase_diff[20:267])
            self.test_id_13219 = numpy.max(self.reverse_s21_phase_diff[7:20]) - numpy.min(self.reverse_s21_phase_diff[7:20])
            self.test_id_13220 = numpy.max(self.reverse_s21_phase_diff[:7]) - numpy.min(self.reverse_s21_phase_diff[:7])
            gui.close()
            logging.info("Fidelity measure completed")
        except Exception:
            gui.set_status("Error occured during fidelity measure, turning off the ATE", 0); logging.warning("Error while performing fidelity measure")
            self.emergency_stop();
            gui.close()
            raise

    def stress(self, sequence):
        try:
            gui = progress_window(f"Stress sequence {sequence}"); logging.info("Starting stress sequence %s measure", sequence)
            gui.set_status("Setting the amplifier in standby", 10); self.comm.standby()
            gui.set_status("Setting the amplifier in body mode", 11); self.comm.body()
            gui.set_status("Making sure that the RF generator is OFF", 6); self.rf.poweroff()
            gui.set_status("Setting the switches", 2); self.sw.config("vna_body")
            gui.set_status("Setting the scope", 4); self.scope.config("")
            gui.set_status("Loading VNA configuration", 6)
            match sequence:
                case 1:
                    self.en.config("0.084", "10.71")
                    self.vna.visa.write(ate_config.load_stress_1)
                case 2:
                    self.en.config("0.089", "20.22")
                    self.vna.visa.write(ate_config.load_stress_2)
                case 3:
                    self.en.config("0.098", "36.73")
                    self.vna.visa.write(ate_config.load_stress_3)
                case 4:
                    self.en.config("0.1", "60")
                    self.vna.visa.write(ate_config.load_stress_4)
                case 5:
                    self.en.config("0.1", "60")
                    self.vna.visa.write(ate_config.load_stress_5)
                case _:
                    logging.warning("Stress sequence %s unknown", sequence)
                    raise RuntimeError(f"Stress sequence {sequence} unknown")
            gui.set_status("Setting the amplifier in operate", 10); self.comm.operate()
            gui.set_status("Turning on blanking signals", 9); self.en.operate()
            gui.set_status("Running stress sequence... (please wait 5 minute)", 10); self.vna_single()
            gui.set_status("Setting the amplifier back to standby", 14); self.comm.standby()
            gui.set_status("Turning off the unblanking generator", 18); self.en.poweroff()
            gui.set_status("Acquiring data from the VNA", 10); s21_raw = self.vna.visa.query("CALC:MEAS1:DATA:FDATa?")
            gui.set_status("Processing VNA data", 98); logging.info("VNA data acquired")
            s21 = numpy.abs(self.vna.parse_data(s21_raw))[30:]
            stress_lin_power = s21**2 / 50
            match sequence:
                case 1:
                    self.stress_1_mag = 20 * numpy.log10(s21)
                    self.test_id_13108 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13108, 2))
                case 2:
                    self.stress_2_mag = 20 * numpy.log10(s21)
                    self.test_id_13109 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13109, 2))
                case 3:
                    self.stress_3_mag = 20 * numpy.log10(s21)
                    self.test_id_13110 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13110, 2))
                case 4:
                    self.stress_4_mag = 20 * numpy.log10(s21)
                    self.test_id_13111 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13111, 2))
                case 5:
                    self.stress_5_mag = 20 * numpy.log10(s21)
                    self.test_id_13112 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13112, 2))
                case _:
                    logging.warning("Stress sequence %s unknown", sequence)
                    raise RuntimeError(f"Stress sequence {sequence} unknown")            
            gui.set_status(f"Stress sequence {sequence} completed" , 100); time.sleep(0.5)
            gui.close()
            logging.info("Stress sequence %s completed", sequence)
        except Exception:
            gui.set_status(f"Error occured during stress sequence {sequence}, turning off the ATE", 0); logging.warning("Error while performing stress sequence %s measure", sequence)
            self.emergency_stop();
            gui.close()
            raise

    def stress_burst(self, sequence):
        try:
            gui = progress_window(f"Stress burst sequence {sequence}"); logging.info("Starting stress burst sequence %s measure", sequence)
            s21 = numpy.array([0])
            gui.set_status("Setting the amplifier in standby", 1); self.comm.standby()
            gui.set_status("Setting the amplifier in body mode", 1); self.comm.body()
            gui.set_status("Making sure that the RF generator is OFF", 1); self.rf.poweroff()
            gui.set_status("Setting the switches", 1); self.sw.config("vna_body")
            gui.set_status("Setting the scope", 1); self.scope.config("")
            gui.set_status("Loading VNA configuration", 1)
            match sequence:
                case 6:
                    self.en.config("0.01", "20")
                    self.vna.visa.write(ate_config.load_stress_6)
                case 7:
                    self.en.config("0.01", "40")
                    self.vna.visa.write(ate_config.load_stress_7)
                case 8:
                    self.en.config("0.01", "60")
                    self.vna.visa.write(ate_config.load_stress_8)
                case _:
                    logging.warning("Stress sequence %s unknown", sequence)
                    raise RuntimeError(f"Stress sequence {sequence} unknown")
            gui.set_status("Setting the amplifier in operate", 10); self.comm.operate()
            gui.set_status("Turning on blanking signals", 9); self.en.operate()
            gui.set_status("Running stress burst sequence... (please wait 5 minute)", 10);
            for i in range(100):
                gui.set_status(f"Running stress sequence ({i}/100)", int(i)); self.vna_single()
                gui.set_status("Acquiring data from the VNA", int(10+i/2)); s21_raw = self.vna.visa.query("CALC:MEAS1:DATA:FDATa?")
                s21_raw_numpy = numpy.abs(self.vna.parse_data(s21_raw))
                if i == 1:
                    s21 = s21_raw_numpy
                else:
                    s21 = numpy.append(s21, s21_raw_numpy)
            gui.set_status("Setting the amplifier back to standby", 100); self.comm.standby()
            gui.set_status("Turning off the unblanking generator", 100); self.en.poweroff()
            gui.set_status("Processing VNA data", 100); logging.info("VNA data acquired")
            stress_lin_power = s21**2 / 50
            match sequence:
                case 6:
                    self.stress_6_mag = 20 * numpy.log10(s21)
                    self.test_id_13113 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13113, 2))
                case 7:
                    self.stress_7_mag = 20 * numpy.log10(s21)
                    self.test_id_13114 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13114, 2))
                case 8:
                    self.stress_8_mag = 20 * numpy.log10(s21)
                    self.test_id_13115 = (numpy.max(stress_lin_power) - numpy.min(stress_lin_power)) / numpy.min(stress_lin_power) * 100
                    logging.info("Stress sequence %s gain variation: %s%%", sequence, round(self.test_id_13115, 2))
                case _:
                    logging.warning("Stress sequence %s unknown", sequence)
                    raise RuntimeError(f"Stress sequence {sequence} unknown")            
            gui.set_status(f"Stress sequence {sequence} completed" , 100); time.sleep(0.5)
            gui.close()
            logging.info("Stress sequence %s completed", sequence)
        except Exception:
            gui.set_status(f"Error occured during stress sequence {sequence}, turning off the ATE", 0); logging.warning("Error while performing stress sequence %s measure", sequence)
            self.emergency_stop();
            gui.close()
            raise
    
    def vna_single(self):
        try:
            self.vna.visa.write("OUTP ON")
            self.vna.visa.write("SENSe:SWEep:MODE SINGle")
            state = ""
            logging.info("VNA is measuring...")
            while state != "HOLD\n":
                time.sleep(1)
                state = self.vna.visa.query("SENSe:SWEep:MODE?")
                self.comm.update()
            self.vna.visa.write("OUTP OFF")
            logging.info("VNA measure ready")
        except COMM_Error as comm_e:
            logging.warning("Error %s occured in the amplifier during VNA measure", hex(comm_e.code))
            raise
        except Exception:
            logging.warning("Error while waiting for VNA to measure")
            raise ATE_Instrument_Error(self.idn) from None

    """ instruments nested class definitions """
    class scope_init:
        def __init__ (self):
            try:
                self.idn = "unknown scope"
                rm = pyvisa.ResourceManager()
                self.visa = rm.open_resource(ate_config.scope_address)
                self.visa.timeout = 20000
                self.idn = self.visa.query("*IDN?").replace('\n', '')
                logging.info("scope found: %s", self.idn)
            except Exception:
                logging.warning("Exception while initializing scope")
                raise ATE_Instrument_Error(self.idn) from None
            
        def config(self, str_config):
            try:
                logging.info("Configuring scope...")
                self.visa.write("*RST")
                self.visa.write("CHANnel1:BANDwidth 350E6")
                self.visa.write("CHANnel1:COUPling DC")
                self.visa.write("CHANnel1:SCALe 0.4")
                self.visa.write("TIMebase:SCALe 1E-3")
                self.visa.write("TIMebase:HORizontal:POSition 0.004")
                self.visa.write("TRIGger:MODE NORMal")
                self.visa.write("TRIGger:ANEDge:LEVel 0.8")
                self.visa.write("TRIGger:ANEDge:COUPling DC")
                self.visa.write("TRIGger:EVENt1:SOURce EXTernanalog")
                self.visa.write("TRIGger:ACTions:OUT:PLENgth 0.008")
                self.visa.write("TRIGger:ACTions:OUT:SOURce ONTRigger")
                self.visa.write("TRIGger:ACTions:OUT:STATe ON")
                self.visa.write("ACQuire:SRAte:MODe MAN")
                self.visa.write("ACQuire:SRAte 5E9")
                self.visa.write("ACQuire:POINTs:MODE MAN")
                self.visa.write("ACQuire:POINTs 50000000")
                
                # self.visa.write("CHANnel4:STATe ON")
                # self.visa.write("CHANnel4:SCALe 0.5")
                
                if str_config == "single_pulse_measure":
                    self.visa.write("TRIGger:MODE SINGLe")
                if str_config == "harmonic_output_measure":
                    self.visa.write("TIMebase:SCALe 0.0005")
                    self.visa.write("ACQuire:POINTs:MODE MAN")
                    self.visa.write("ACQuire:POINTs 25000000")
                    self.visa.write("TRIGger:MODE SINGLe")
                    self.visa.write("CALCulate:SPECtrum1:STATe ON")
                    self.visa.write("CALCulate:SPECtrum1:SOURce C1")
                    self.visa.write("CALCulate:SPECtrum1:FREQuency:STARt 50E6")
                    self.visa.write("CALCulate:SPECtrum1:FREQuency:STOP 300E6")
                    self.visa.write("CALCulate:SPECtrum1:GATE:POSition 0.004")
                    self.visa.write("CALCulate:SPECtrum1:GATE:WIDTh 0.002")
                if str_config == "noise_unblanked_measure":
                    self.visa.write("CHANnel1:SCALe 0.001")
                    self.visa.write("TIMebase:SCALe 0.002")
                    self.visa.write("TIMebase:HORizontal:POSition 0.01")
                    self.visa.write("CALCulate:SPECtrum1:STATe ON")
                    self.visa.write("CALCulate:SPECtrum1:SOURce C1")
                    self.visa.write("CALCulate:SPECtrum1:MAGNitude:LEVel -70")
                    self.visa.write("CALCulate:SPECtrum1:FREQuency:STARt 63.585E6")
                    self.visa.write("CALCulate:SPECtrum1:FREQuency:STOP 64.135E6")
                    self.visa.write("CALCulate:SPECtrum1:GATE:POSition 0.01")
                    self.visa.write("CALCulate:SPECtrum1:GATE:WIDTh 0.02")
                    self.visa.write("TRIGger:MODE SINGLe")
                self.visa.query("*OPC?")
                logging.info("Scope configured")
            except Exception:
                logging.warning("Exception while configuring the scope")
                raise ATE_Instrument_Error(self.idn) from None
        
        def visa_binary(self, data):
            try:
                header_len = int(chr(data[1]))
                num_bytes = int(data[2:2+header_len].decode('ascii'))
                payload = data[2+header_len:2+header_len+num_bytes]
                waveform = numpy.frombuffer(payload, dtype=numpy.float64)
                return waveform
            except Exception:
                logging.warning("Exception while processing scope data")
                raise ATE_Instrument_Error(self.idn) from None
            
        def single_trigger(self):
            try:
                logging.info("Waiting for the scope to trigger...")
                self.visa.query("RUNSINGle;*OPC?")
                logging.info("Scope triggered")
            except Exception:
                logging.warning("Exception while trying to trigger the scope")
                raise ATE_Instrument_Error(self.idn) from None
            
    class vna_init:
        def __init__ (self):
            try:
                self.idn = "unknown VNA"
                rm = pyvisa.ResourceManager()
                self.visa = rm.open_resource(ate_config.vna_address)
                self.visa.timeout = 5000
                self.idn = self.visa.query("*IDN?").replace('\n', '')
                logging.info("Network analyzer found: %s", self.idn)
            except Exception:
                logging.warning("Error while initializing the network analyzer")
                raise ATE_Instrument_Error(self.idn) from None
        
        def operate (self):
            try:
                self.vna.visa.write("OUTP ON")
            except Exception:
                logging.warning("Error while turning on the network analyzer")
                raise ATE_Instrument_Error(self.idn) from None
        
        def poweroff(self):
            try:
                self.visa.write("OUTP OFF")
                self.visa.query("*OPC?")
                logging.info("Network analyzer OFF")
            except Exception:
                logging.warning("Error while turning off the network analyzer")
                raise ATE_Instrument_Error(self.idn) from None
        
        def parse_data(self, raw):
            try:
                data = [float(x) for x in raw.strip().split(',')]
                return numpy.array(data[::2]) + 1j * numpy.array(data[1::2])
            except Exception:
                logging.warning("Error while processing VNA data")
                raise ATE_Instrument_Error(self.idn) from None

    class en_init:
        def __init__ (self):
            try:
                self.idn = "unknown unblanking generator"
                rm = pyvisa.ResourceManager()
                self.visa = rm.open_resource(ate_config.en_address)
                self.visa.timeout = 5000
                self.idn = self.visa.query("*IDN?").replace('\n', '')
                logging.info("Unblanking generator found: %s", self.idn)
            except Exception:
                logging.warning("Error while initializing blanking waveform generator")
                raise ATE_Instrument_Error(self.idn) from None
        
        def poweroff (self):
            try:
                self.visa.write("OUTPUT1 OFF")
                self.visa.write("OUTPUT2 OFF") 
                self.visa.query("*OPC?")
                logging.info("Unblanking generator OFF")
            except Exception:
                logging.warning("Exception occured while switching off the unblanking generator")
                raise ATE_Instrument_Error(self.idn) from None
            
        def operate (self):
            try:
                self.visa.write("OUTPUT2 ON")
                self.visa.write("OUTPUT1 ON")
                self.visa.query("*OPC?")
            except Exception:
                logging.warning("Exception occured while turning on the unblanking generator")
                raise ATE_Instrument_Error(self.idn) from None
            
        def config (self, period, duty_cycle):
            try:
                logging.info("Configuring unblanking generator...")
                self.visa.write("*RST")
                self.visa.write("SOURce1:TRACk INVerted")
                self.visa.write("OUTPut1:LOAD INFinity")
                self.visa.write("SOURce1:FUNCtion SQUare")
                self.visa.write("SOURce1:VOLTage:LOW 0")
                self.visa.write("SOURce1:VOLTage:HIGH 5")
                self.visa.write(f"FUNCTION:SQUARE:PERIOD {period}")
                self.visa.write(f"SOURce1:FUNCtion:SQUare:DCYCle {duty_cycle}")
                self.visa.query("*OPC?")
                logging.info("Unblanking generator ON")
            except Exception:
                logging.warning("Exception occured while configuring the unblanking generator")
                raise ATE_Instrument_Error(self.idn) from None
        
    class rf_init:
        def __init__ (self):
            try:
                rm = pyvisa.ResourceManager()
                self.visa = rm.open_resource(ate_config.rf_address)
                self.visa.timeout = 5000
                self.idn = self.visa.query("*IDN?").replace('\n', '')
                logging.info("RF generator found: %s", self.idn)
            except Exception:
                logging.warning("Exception occured while initializing the RF generator")
                raise ATE_Instrument_Error(self.idn) from None
        
        def operate (self):
            try:
                self.visa.write("OUTPUT1 ON")
                self.visa.query("*OPC?")
            except Exception:
                logging.warning("Exception occured while turning on the RF generator")
                raise ATE_Instrument_Error(self.idn) from None
        
        def config (self, dBm):
            try:
                logging.info("Configuring RF generator... ")
                self.visa.write("*RST")
                self.visa.write("OUTPut1:LOAD 50")
                self.visa.write("SOURce1:FUNCtion SIN")
                self.visa.write("SOURCE1:FREQUENCY 63860000")
                self.visa.write("SOURCE1:VOLT:UNIT DBM")
                self.visa.write(f"SOURCE1:VOLT {dBm}")
                self.visa.write("SOURCE1:BURST:MODE GAT")
                self.visa.write("SOURCE1:BURST:STATE ON")
                self.visa.write("TRIGger1:DELay 1E-4")
                self.visa.query("*OPC?")
                logging.info("RF generator ON")
            except Exception:
                logging.warning("Exception occured while configuring the RF generator")
                raise ATE_Instrument_Error(self.idn) from None
            
        def poweroff (self):
            try:
                self.visa.write("OUTPUT1 OFF")
                logging.info("RF generator OFF")
            except Exception:
                logging.warning("Exception occured while turning off the RF generator")
                raise ATE_Instrument_Error(self.idn) from None
        
    class sw_init:
        def __init__ (self):
            try:
                self.idn = "unknown switches"
                logging.info("Switches found: %s", self.idn)
            except Exception:
                logging.warning("Exception occured while initializing the switches")
                raise ATE_Instrument_Error(self.idn) from None
            
        def config (self, config_name):
            try:
                match config_name:
                    case "scope_body":
                        logging.info("Switching to SCOPE/BODY measure")
                        # self.visa.write("SETP=0")
                    case "scope_head":
                        logging.info("Switching to SCOPE/HEAD measure")
                        # self.visa.write("SETP=2")
                    case "vna_body":
                        logging.info("Switching to VNA/BODY measure")
                        # self.visa.write("SETP=5")
                    case "vna_head":
                        logging.info("Switching to VNA/HEAD measure")
                        # self.visa.write("SETP=7")
                    case _:
                        logging.warning("Switch configuration", config_name, "unknown")
                        raise RuntimeError("Switch configuration %s unknown", config_name)
                        # self.visa.write("SETP=0")
            except Exception:
                logging.warning("Exception occured while configuring the switches")
                raise ATE_Instrument_Error(self.idn) from None
    
    class comm_init:
        def __init__ (self):
            try:
                rm_rs232 = pyvisa.ResourceManager('@py')
                self.visa = rm_rs232.open_resource(ate_config.comm_address)
                self.visa.baud_rate = 9600
                self.visa.data_bits = 8
                self.visa.stop_bits = pyvisa.constants.StopBits.one
                self.visa.parity = pyvisa.constants.Parity.none
                self.visa.timeout = 2000
            except Exception:
                logging.warning("Exception occured while initializing the amplifier COMM interface")
                raise
            
        def command (self, the_command):
            try:
                self.visa.write(the_command)
                self.visa.read()
                return self.visa.read().replace('\r', '').replace('>', '').replace('\n', '')
            except Exception:
                logging.warning("Exception occured while using the amplifier COMM interface")
                raise ATE_Instrument_Error("COMM") from None
        
        def update (self):
            logging.debug("Reading amplifier registers")
            reg3011 = int(self.command("MR3011\n"), 16)
            self.wait = (reg3011 & 0b00000100) >> 2; 
            self.state = (reg3011 & 0b00011000) >> 3
            self.watchdog = (reg3011 & 0b00100000) >> 5
            self.operate_low = (reg3011 & 0b01000000) >> 6
            self.fault = (reg3011 & 0b10000000) >> 7
            self.mode = (int(self.command("MR3012\n"), 16) & 0b01100000) >> 5
            self.frequency = int(self.command("MR3013\n"), 16)
            self.error = int(self.command("MR3014\n"), 16)
            logging.debug("wait:%s, state:%s, watchdog:%s, operate_low:%s, fault:%s, mode:%s, frequency:%s, error:%s", self.wait, self.state, self.watchdog, self.operate_low, self.fault, self.mode, self.frequency, self.error)
            if self.fault == 1:
                logging.error("COMM error: %s", hex(self.error))
                raise COMM_Error(self.error)
        
        def poweroff (self):
            self.command("MW3001 00\n")
            logging.info("Transiting to POWER OFF state ")
            self.wait_state(0)
            logging.info("Amp in POWER OFF state")
            
        def standby(self):
            self.command("MW3001 01\n")
            logging.info("Transiting to STANDBY state ")
            self.wait_state(1)
            logging.info("Amp in STANDBY state")

        def operate(self):
            self.update()
            if self.state == 0:
                self.standby()
            self.command("MW3001 03\n")
            logging.info("Transiting to OPERATE state ") 
            self.wait_state(3)
            logging.info("Amp in OPERATE state")
            
        def wait_state (self, state):
            count = 0
            self.update()
            while (self.state != state) or (self.wait == 1):
                time.sleep(0.5)
                self.update()
                count += 1
                if count > 20:
                    logging.warning("The RF amplifier took more than 10 seconds to switch state")
                    raise RuntimeError("The RF amplifier took more than 10 seconds to switch state")
            time.sleep(0.5)
                
        def wait_mode (self, mode):
            count = 0
            self.update()
            while (self.mode != mode) or (self.wait == 1):
                time.sleep(0.5)
                self.update()
                count += 1
                if count > 20:
                    logging.warning("The RF amplifier took more than 10 seconds to switch mode")
                    raise RuntimeError("The RF amplifier took more than 10 seconds to switch mode")
            time.sleep(0.5)
            
        def body (self):
            self.command("MW3002 60\n")
            self.wait_mode(3)
            logging.info("BODY output selected")
            
        def head (self):
            self.command("MW3002 40\n")
            self.wait_mode(2)
            logging.info("HEAD output selected")
            
        def test (self):
            self.command("MW3002 20\n")
            self.wait_mode(1)
            logging.info("TEST output selected")
            
    class amp_init:
        def __init__ (self, master_slave):
            try:
                rm_rs232 = pyvisa.ResourceManager('@py')
                if master_slave == "master":
                    self.visa = rm_rs232.open_resource(ate_config.master_address)
                elif master_slave == "slave":
                    self.visa = rm_rs232.open_resource(ate_config.slave_address)
                self.visa.baud_rate = 9600
                self.visa.data_bits = 8
                self.visa.stop_bits = pyvisa.constants.StopBits.one
                self.visa.parity = pyvisa.constants.Parity.none
                self.visa.timeout = 2000
                self.name = master_slave
            except Exception:
                logging.warning("Exception occured while initializing the %s amplifier")
                raise
            
        def command (self, the_command):
            try:
                self.visa.write(the_command)
                self.visa.read()
                return self.visa.read().replace('\r', '').replace('>', '').replace('\n', '')
            except Exception:
                logging.warning("Exception occured while using the %s amplifier interface", self.name)
                raise
            
        def password (self):
            self.command("PASS drowssap\n")
            
        def set_gain(self, gain):
            self.password()
            self.command(f"DAC 37 {gain}\n")
            self.visa.write("EE:STOre:RF\n")
            time.sleep(0.1)
            self.visa.read()
            time.sleep(0.1)
            self.visa.read()
            time.sleep(0.1)
            
        def help(self):
            self.password()
            logging.info("Help of %s amplifier:", self.name)
            self.visa.write("HELP?\n")
            msg = self.visa.read()
            while msg != "\rPress a key\r\n":
                logging.info("%s", msg.replace('\n', ''))
                msg = self.visa.read() 
            self.visa.write("\n")
            msg = self.visa.read()
            while msg != "\rPress a key\r\n":
                logging.info("%s", msg.replace('\n', ''))
                msg = self.visa.read()
            self.visa.write("\n")
            msg = self.visa.read()
            while msg != "\r\n":
                logging.info("%s", msg)
                msg = self.visa.read()

        def update_fault(self):
            self.fault = self.command("FAULT?\n")
            logging.info("%s FAULT?: %s", self.name, self.fault)
            
        def update_meas(self):
            self.command("MEAS?\n")
            self.meas = self.visa.read().replace('\r', '').replace('>', '').replace('\n', '')
            logging.info("%s MEAS?: %s", self.name, self.meas)
            self.temp1, self.temp2, self.power, self.current, self.alim_140, self.alim_48, self.alim_p15, self.alim_m15 = [float(token.rstrip('WVCmA')) for token in self.meas.split()] 
            
        def update_mode(self):
            self.mode = self.command("MODE?\n")
            logging.info("%s MODE?: %s", self.name, self.mode)
            
        def bias(self):
            try:
                logging.info("reading bias of %s amp", self.name)
                self.visa.write("BIAS:MEAS? 0\n")
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.biasQ3, self.biasQ4, self.biasQ5, self.biasQ6, self.biasQ7, self.biasQ8, self.biasQ9, self.biasQ10 = [int(token) for token in raw_str.split()]
                logging.info("biasQ3:%s, biasQ4:%s, biasQ5:%s, biasQ6:%s, biasQ7:%s, biasQ8:%s, biasQ9:%s, biasQ10:%s", self.biasQ3, self.biasQ4, self.biasQ5, self.biasQ6, self.biasQ7, self.biasQ8, self.biasQ9, self.biasQ10)
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.biasQ11, self.biasQ12, self.biasQ13, self.biasQ14, self.biasQ15, self.biasQ16, self.biasQ17, self.biasQ18 = [int(token) for token in raw_str.split()]
                logging.info("biasQ11:%s, biasQ12:%s, biasQ13:%s, biasQ14:%s, biasQ15:%s, biasQ16:%s, biasQ17:%s, biasQ18:%s", self.biasQ11, self.biasQ12, self.biasQ13, self.biasQ14, self.biasQ15, self.biasQ16, self.biasQ17, self.biasQ18)
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.biasQ19, self.biasQ20, self.biasQ21, self.biasQ22, self.biasQ23, self.biasQ24, self.biasQ25, self.biasQ26 = [int(token) for token in raw_str.split()]
                logging.info("biasQ19:%s, biasQ20:%s, biasQ21:%s, biasQ22:%s, biasQ23:%s, biasQ24:%s, biasQ25:%s, biasQ26:%s", self.biasQ19, self.biasQ20, self.biasQ21, self.biasQ22, self.biasQ23, self.biasQ24, self.biasQ25, self.biasQ26)
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.biasQ27, self.biasQ28, self.biasQ34, self.biasQ35, self.biasQ33, self.biasQ31, self.biasQ32 = [int(token) for token in raw_str.split()]
                logging.info("biasQ27:%s, biasQ28:%s, biasQ34:%s, biasQ35:%s, biasQ33:%s, biasQ31:%s, biasQ32:%s", self.biasQ27, self.biasQ28, self.biasQ34, self.biasQ35, self.biasQ33, self.biasQ31, self.biasQ32)
                self.visa.read()
                self.visa.read()
            except Exception:
                logging.warning("Exception occured while reading the %s amplifier bias", self.name)
                raise
            
        def dac(self):
            try:
                self.password()
                logging.info("reading dac of %s amp", self.name)
                self.visa.write("DAC? *\n")
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.dacQ3, self.dacQ4, self.dacQ5, self.dacQ6, self.dacQ7, self.dacQ8, self.dacQ9, self.dacQ10, self.dacQ11, self.dacQ12, self.dacQ13, self.dacQ14 = [int(token) for token in raw_str.split()]
                logging.info("dacQ3:%s, dacQ4:%s, dacQ5:%s, dacQ6:%s, dacQ7:%s, dacQ8:%s, dacQ9:%s, dacQ10:%s, dacQ11:%s, dacQ12:%s, dacQ13:%s, dacQ14:%s", self.dacQ3, self.dacQ4, self.dacQ5, self.dacQ6, self.dacQ7, self.dacQ8, self.dacQ9, self.dacQ10, self.dacQ11, self.dacQ12, self.dacQ13, self.dacQ14)
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.dacQ15, self.dacQ16, self.dacQ17, self.dacQ18, self.dacQ19, self.dacQ20, self.dacQ21, self.dacQ22, self.dacQ23, self.dacQ24, self.dacQ25, self.dacQ26 = [int(token) for token in raw_str.split()]
                logging.info("dacQ15:%s, dacQ16:%s, dacQ17:%s, dacQ18:%s, dacQ19:%s, dacQ20:%s, dacQ21:%s, dacQ22:%s, dacQ23:%s, dacQ24:%s, dacQ25:%s, dacQ26:%s", self.dacQ15, self.dacQ16, self.dacQ17, self.dacQ18, self.dacQ19, self.dacQ20, self.dacQ21, self.dacQ22, self.dacQ23, self.dacQ24, self.dacQ25, self.dacQ26)
                self.visa.read()
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                raw_str = self.visa.read().replace('\r', '').replace('\n', ''); logging.debug("%s", raw_str)
                self.dacQ27, self.dacQ28, self.dacQ34, self.dacQ35, self.dacQ33, self.dacQ31, self.dacQ32, self.Gai, self.HS, self.TJ = [int(token) for token in raw_str.split()]
                logging.info("dacQ27:%s, dacQ28:%s, dacQ34:%s, dacQ35:%s, dacQ33:%s, dacQ31:%s, dacQ32:%s, Gai:%s, HS:%s, TJ:%s", self.dacQ27, self.dacQ28, self.dacQ34, self.dacQ35, self.dacQ33, self.dacQ31, self.dacQ32, self.Gai, self.HS, self.TJ)
                self.visa.read()
            except Exception:
                logging.warning("Exception occured while reading the %s amplifier dac", self.name)
                raise
        
        def auto_bias(self):
            try:
                logging.info("Starting autobias of %s amp", self.name)
                self.password()
                self.command("BIAS:AUTO\n")
                self.visa.read()
                time.sleep(1)
                self.command("EE:STO:RF\n")
                logging.info("Autobias successfull", self.name)
            except Exception:
                logging.warning("Exception occured while running autobias on the %s amplifier", self.name)
                raise

""" GUI definitions """         
class progress_window:
    def __init__(self, wtitle, wsize=400, x=520, y=410):
        if tkinter._default_root is None:
            self.root = tkinter.Tk()
        else:
            self.root = tkinter.Toplevel(tkinter._default_root)
        self.root.overrideredirect(True)
        self.root.geometry(f"{wsize}x125+{x}+{y}")
        self.title_var = tkinter.StringVar(value=wtitle)
        self.title_label = tkinter.ttk.Label(self.root, textvariable=self.title_var, anchor="w", font=tkinter.font.Font(family="Sergoe UI", size=12, weight="bold"))
        self.title_label.pack(padx=20,pady=(20,0),  fill="x")
        self.progress = tkinter.ttk.Progressbar(self.root, length=(wsize-40), mode="determinate", maximum=100)
        self.progress.pack(pady=(10,0))
        self.status_var = tkinter.StringVar(value="Starting...")
        self.status_label = tkinter.ttk.Label(self.root, textvariable=self.status_var, anchor="w", font=tkinter.font.Font(family="Sergoe UI", size=10))
        self.status_label.pack(padx=20, pady=(10,0), fill="x")
        self.root.update_idletasks()
        self.root.update()
    def set_status(self, text: str, value: int):
        self.status_var.set(text)
        self.progress["value"] = value
        self.root.update_idletasks()
        self.root.update()
    def close(self):
        self.root.destroy()