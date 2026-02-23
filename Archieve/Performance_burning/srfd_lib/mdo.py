import pyvisa
import sys
import time
import numpy
import scipy.fft
import math
import csv
from Performance_burning.srfd_lib.amp import amp_operate, amp_standby, body_mode  
from Performance_burning.srfd_lib.swg import swg_on, swg_off, swg_config_harmonic_output, swg_config_single_pulse, swg_config_intermodulation, swg_config_fidelity  



def single_trigger_mdo4054(scope):
    print("Waiting for trigger", end="")
    sys.stdout.flush()
    
    scope.write("ACQuire:STATE RUN")
    scope.write("ACQuire:STOPAfter SEQuence")
    while True:
        print(".", end="")
        sys.stdout.flush()
        state = scope.query("TRIGger:STATE?").strip()
        if state == "SAVE":
            print(" triggered")
            break
        time.sleep(1)




def get_channel_data_mdo4054(scope, nbrpoint, channel):
    print("Getting scope data", end="")
    sys.stdout.flush()
    
    # Set up waveform transfer
    scope.write("DATa:WIDth 1")
    scope.write("DATa:ENCdg ASCII")
    scope.write(f"SELect:CH{channel} ON")
    scope.write(f"DATa:SOUrce CH{channel}")
    chunk_size = 1000000
    print(".", end="")
    sys.stdout.flush()
    
    
    #get scaling parameters
    preamble = scope.query("WFMOutpre?")
    x_increment = float(scope.query("WFMOutpre:XINcr?"))
    x_zero = float(scope.query("WFMOutpre:XZERo?"))
    y_mult = float(scope.query("WFMOutpre:YMUlt?"))
    y_zero = float(scope.query("WFMOutpre:YZERo?"))
    y_offset = float(scope.query("WFMOutpre:YOFf?"))
    print(".", end="")
    sys.stdout.flush()
    
    # Get waveform data
    ch_data = []
    for start in range(1, nbrpoint + 1, chunk_size):
        stop = min(start + chunk_size - 1, nbrpoint)
        scope.write(f"DATa:STARt {start}")
        scope.write(f"DATa:STOP {stop}")
        raw_chunk = scope.query("CURVe?")
        chunk_data = [int(val) for val in raw_chunk.strip().split(',')]
        ch_data.extend(chunk_data)
        print(".", end="")
        sys.stdout.flush()
    ch_data = numpy.array(ch_data)

    ch_voltages = y_zero + y_mult * (ch_data - y_offset)
    times = x_zero + x_increment * numpy.arange(len(ch_voltages))
    print(" done")
    return times, ch_voltages    



def cycle_rms(signal, sampling_rate):
    # Step 1: Estimate the fundamental frequency using FFT
    N = len(signal)
    yf = scipy.fft.rfft(signal)
    xf = scipy.fft.rfftfreq(N, 1 / sampling_rate)

    # Ignore DC component and find peak frequency
    magnitude = numpy.abs(yf)
    magnitude[0] = 0  # remove DC
    peak_index = numpy.argmax(magnitude)
    fundamental_freq = xf[peak_index]

    # Step 2: Calculate the period in samples
    period_samples = int(sampling_rate / fundamental_freq)

    # Step 3: Segment the signal into cycles
    num_cycles = N // period_samples
    rms_values = []

    for i in range(num_cycles):
        cycle = signal[i * period_samples : (i + 1) * period_samples]
        rms = numpy.sqrt(numpy.mean(cycle ** 2))
        rms_values.append(rms)

    return rms_values
    
def single_pulse_measure_mdo4054 (mdo4054, swg33522B, swg33611A, srfd_com):
    print()
    print("Starting single pulse measure")
    sys.stdout.flush()
    mdo4054.write("*RST")
    mdo4054.write("CH1:SCAle 0.5")
    mdo4054.write("CH1:POSition 0")
    mdo4054.write("CH1:TERmination FIFty")
    mdo4054.write("SELect:CH1 ON")
    mdo4054.write("CH4:SCAle 0.5")
    mdo4054.write("CH4:POSition -3.3")
    mdo4054.write("CH4:TERmination MEG")
    mdo4054.write("SELect:CH4 ON")
    mdo4054.write("TRIGger:A:TYPe EDGE")
    mdo4054.write("TRIGger:A:EDGE:SOUrce CH4")
    mdo4054.write("TRIGger:A:LEVel:CH4 1.65")
    mdo4054.write("TRIGger:A:EDGE:SLOpe RISE")
    mdo4054.write("TRIGger:A:EDGE:COUPling DC")
    mdo4054.write("HORizontal:RECOrdlength 5000000")
    mdo4054.write("HORizontal:SCAle 0.0002")
    mdo4054.write("HORizontal:DELay:TIMe 0.0018")
    mdo4054.write("ACQuire:MODe SAMple")
    mdo4054.query("*OPC?")
    swg_config_single_pulse(swg33522B, swg33611A)
    amp_standby(srfd_com)
    swg_on(swg33522B, swg33611A)
    body_mode(srfd_com)
    amp_operate(srfd_com)
    single_trigger_mdo4054(mdo4054)
    amp_standby(srfd_com)
    swg_off(swg33522B, swg33611A)
    time_ch1, data_ch1 = get_channel_data_mdo4054(mdo4054, 5000000, 1)
    print("Processing single pulse data... ", end="")
    sys.stdout.flush()
    crms_ch1 = cycle_rms(data_ch1, 2500000000)
    print("done")
    min_rms = numpy.min(crms_ch1)
    max_rms = numpy.max(crms_ch1)
    output_power = 10 * math.log10( numpy.mean(crms_ch1)**2 / 50 ) + 60 + 30
    gain_variation = 20 * math.log10(max_rms / min_rms)
    return gain_variation, output_power




    

def harmonic_output_measure_mdo4054 (mdo4054, swg33522B, swg33611A, srfd_com):
    print()
    print("Starting harmonic output measure")
    sys.stdout.flush()
    mdo4054.write("*RST")
    mdo4054.write("CH1:SCAle 0.5")
    mdo4054.write("CH1:POSition 0")
    mdo4054.write("CH1:TERmination FIFty")
    mdo4054.write("SELect:CH1 ON")
    mdo4054.write("CH4:SCAle 0.5")
    mdo4054.write("CH4:POSition -3.3")
    mdo4054.write("CH4:TERmination MEG")
    mdo4054.write("SELect:CH4 OFF")
    mdo4054.write("TRIGger:A:TYPe EDGE")
    mdo4054.write("TRIGger:A:EDGE:SOUrce CH4")
    mdo4054.write("TRIGger:A:LEVel:CH4 1.65")
    mdo4054.write("TRIGger:A:EDGE:SLOpe RISE")
    mdo4054.write("TRIGger:A:EDGE:COUPling DC")
    mdo4054.write("HORizontal:RECOrdlength 1000000")
    mdo4054.write(f"HORizontal:SCAle 0.00004")
    mdo4054.write(f"HORizontal:DELay:TIMe 0.0018")
    mdo4054.write("ACQuire:MODe SAMple")
    swg_config_harmonic_output (swg33522B, swg33611A)
    amp_standby(srfd_com)
    swg_on(swg33522B, swg33611A)
    body_mode(srfd_com)
    amp_operate(srfd_com)
    single_trigger_mdo4054(mdo4054)
    amp_standby(srfd_com)
    swg_off(swg33522B, swg33611A)
    mdo4054.write("SELECT:MATH ON")
    mdo4054.write("MATH:DEFINE \"FFT(CH1)\"")
    print("Waiting for MATH to be calculated.", end="")
    sys.stdout.flush()
    for i in range(7):
        time.sleep(1)
        print(".", end="")
        sys.stdout.flush()
    print(" done")
    mdo4054.write("DATA:SOURCE MATH")
    mdo4054.write("DATa:WIDth 1")
    mdo4054.write("DATa:ENCdg ASCII")
    mdo4054.write("DATa:STARt 1")
    mdo4054.write("DATa:STOP 1000000")
    raw_fft_data = mdo4054.query("CURVE?")
    fft_data = list(map(float, raw_fft_data.split(',')))
    fft_data_array_harmonic = numpy.array(fft_data)
    fondamental_array = fft_data_array_harmonic[25000:75000]
    harmoniques_array = fft_data_array_harmonic[75000:]
    fondamental = numpy.max(fondamental_array)
    harmonique = numpy.max(harmoniques_array)
    harmonic_output = abs(fondamental - harmonique)
    return harmonic_output





def fidelity_test_mdo4054 (mdo4054, swg33522B, swg33611A, srfd_com):
    
    print()
    print("Starting device configuration for fidelity test")
    sys.stdout.flush()
    mdo4054.write("*RST")
    mdo4054.write("CH1:SCAle 0.26")
    mdo4054.write("CH1:POSition 0")
    mdo4054.write("CH1:TERmination FIFty")
    mdo4054.write("SELect:CH1 ON")
    mdo4054.write("CH4:SCAle 0.5")
    mdo4054.write("CH4:POSition -3.3")
    mdo4054.write("CH4:TERmination MEG")
    mdo4054.write("SELect:CH4 ON")
    mdo4054.write("TRIGger:A:TYPe EDGE")
    mdo4054.write("TRIGger:A:EDGE:SOUrce CH4")
    mdo4054.write("TRIGger:A:LEVel:CH4 1.65")
    mdo4054.write("TRIGger:A:EDGE:SLOpe RISE")
    mdo4054.write("TRIGger:A:EDGE:COUPling DC")
    mdo4054.write("HORizontal:RECOrdlength 20000000")
    mdo4054.write("HORizontal:SCAle 0.0008")
    mdo4054.write("HORizontal:DELay:TIMe 0.00455")
    mdo4054.write("ACQuire:MODe SAMple")
    mdo4054.query("*OPC?")
    swg_config_fidelity (swg33522B, swg33611A)
    amp_standby(srfd_com)
    swg_on(swg33522B, swg33611A)
    body_mode(srfd_com)
    amp_operate(srfd_com)
    print("Waiting for the amplifier to heat up", end="")
    for i in range(20):
        time.sleep(1)
        print(".", end="")
        sys.stdout.flush()
    print(" done")
    print("getting first sample")
    single_trigger_mdo4054(mdo4054)
    times1, ch_voltages1 = get_channel_data_mdo4054(mdo4054, 20000000, 1)
    print("getting second sample")
    single_trigger_mdo4054(mdo4054)
    times2, ch_voltages2 = get_channel_data_mdo4054(mdo4054, 20000000, 1)
    print("getting third sample")
    single_trigger_mdo4054(mdo4054)
    times3, ch_voltages3 = get_channel_data_mdo4054(mdo4054, 20000000, 1)
    print("getting fourth sample")
    single_trigger_mdo4054(mdo4054)
    times4, ch_voltages4 = get_channel_data_mdo4054(mdo4054, 20000000, 1)
    amp_standby(srfd_com)
    swg_off(swg33522B, swg33611A)
    print("saving in csv file...", end="")
    sys.stdout.flush()
    with open("C:\\Users\\NP700007626\\Downloads\\data.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time (s)', 'Voltage 1 (V)', 'Voltage 2 (V)', 'Voltage 3 (V)', 'Voltage 4 (V)'])
        for t1, v1, v2, v3, v4 in zip(times1, ch_voltages1, ch_voltages2, ch_voltages3, ch_voltages4):
            writer.writerow([t1, v1, v2, v3, v4])
    print(" done")


def intermodulation_measure_mdo4054 (mdo4054, swg33522B, swg33611A, srfd_com):
    print()
    print("Starting intermodulation measure", end="")
    sys.stdout.flush()
    mdo4054.write("*RST")
    mdo4054.write("CH1:SCAle 0.5")
    mdo4054.write("CH1:POSition 0")
    mdo4054.write("CH1:TERmination FIFty")
    mdo4054.write("SELect:CH1 ON")
    mdo4054.write("CH4:SCAle 0.5")
    mdo4054.write("CH4:POSition -3.3")
    mdo4054.write("CH4:TERmination MEG")
    mdo4054.write("SELect:CH4 OFF")
    mdo4054.write("TRIGger:A:TYPe EDGE")
    mdo4054.write("TRIGger:A:EDGE:SOUrce CH4")
    mdo4054.write("TRIGger:A:LEVel:CH4 1.65")
    mdo4054.write("TRIGger:A:EDGE:SLOpe RISE")
    mdo4054.write("TRIGger:A:EDGE:COUPling DC")
    mdo4054.write("HORizontal:RECOrdlength 1000000")
    mdo4054.write(f"HORizontal:SCAle 0.00004")
    mdo4054.write(f"HORizontal:DELay:TIMe 0.0018")
    mdo4054.write("ACQuire:MODe SAMple")
    swg_config_intermodulation(swg33522B, swg33611A)
    amp_standby(srfd_com)
    swg_on(swg33522B, swg33611A)
    body_mode(srfd_com)
    amp_operate(srfd_com)
    single_trigger_mdo4054(mdo4054)
    amp_standby(srfd_com)
    swg_off(swg33522B, swg33611A)
    mdo4054.write("SELECT:MATH ON")
    mdo4054.write("MATH:DEFINE \"FFT(CH1)\"")
    print("Waiting for MATH to be calculated.", end="")
    sys.stdout.flush()
    for i in range(7):
        time.sleep(1)
        print(".", end="")
        sys.stdout.flush()
    print(" done")
    mdo4054.write("DATA:SOURCE MATH")
    mdo4054.write("DATa:WIDth 1")
    mdo4054.write("DATa:ENCdg ASCII")
    mdo4054.write("DATa:STARt 1")
    mdo4054.write("DATa:STOP 1000000")
    raw_fft_data = mdo4054.query("CURVE?")
    fft_data = list(map(float, raw_fft_data.split(',')))
    fft_data_array = numpy.array(fft_data)
    intermodul_array = numpy.concatenate((fft_data_array[50500:51050],fft_data_array[51130:51800]))
    fondamental = numpy.max(fft_data_array)
    intermodul = numpy.max(intermodul_array)
    intermodulation = fondamental - intermodul
    return intermodulation
