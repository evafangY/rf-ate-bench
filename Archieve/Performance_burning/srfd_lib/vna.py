import numpy
from Performance_burning.srfd_lib import amp
from Performance_burning.srfd_lib import swg
from Performance_burning.srfd_lib import mxo
import csv
import matplotlib.pyplot
import time

def parse_data(raw):
    data = [float(x) for x in raw.strip().split(',')]
    return numpy.array(data[::2]) + 1j * numpy.array(data[1::2])

def wait_for_single(p5000a):
    state = ""
    while state != "HOLD\n":
        time.sleep(0.5)
        state = p5000a.query("SENSe:SWEep:MODE?")

def gain_flatness(p5000a, srfd_com, swg33522B, swg33611A, mxo3):
    print()
    print("Starting gain flatness measure")
    amp.standby(srfd_com)
    amp.body_mode(srfd_com)
    swg.config_vna(swg33522B)
    mxo.config_vna(mxo3)
    swg.on(swg33522B, swg33611A)
    p5000a.write(r'MMEM:LOAD:FILE "C:\Users\NP700007626\Desktop\routines\states\gain_flatness.csa"')
    amp.operate(srfd_com)
    p5000a.write("OUTP ON")
    p5000a.write("SENSe:SWEep:MODE SINGle")
    wait_for_single(p5000a)
    s11_raw = p5000a.query("CALC:MEAS1:DATA:FDATa?") #parametre S11 -> Trace 1 dans le fichier .csa
    s21_raw = p5000a.query("CALC:MEAS2:DATA:FDATa?") #parametre S21 -> Trace 2 dans le fichier .csa
    p5000a.write("OUTP OFF")
    amp.standby(srfd_com)
    swg.off(swg33522B, swg33611A)
    s11 = numpy.abs(parse_data(s11_raw))
    s21_mag = 20 * numpy.log10(numpy.abs(parse_data(s21_raw)))
    freq = numpy.linspace(63585000, 64135000, 101)

    # visualisation 
    matplotlib.pyplot.figure(num="s11")
    matplotlib.pyplot.plot(freq, 20 * numpy.log10(s11))
    matplotlib.pyplot.figure(num="gain flatness")
    matplotlib.pyplot.plot(freq, s21_mag)

    s11_max = numpy.max(s11)
    vswr = (1 + s11_max) / (1 - s11_max)
    flatness = numpy.max(s21_mag) - numpy.min(s21_mag)
    
    return vswr, flatness
    
def amplification(p5000a, srfd_com, swg33522B, swg33611A, mxo3):
    print()
    print("Starting amplification fidelity measure")
    amp.standby(srfd_com)
    amp.body_mode(srfd_com)
    swg.config_vna(swg33522B)
    mxo.config_vna(mxo3)
    swg.on(swg33522B, swg33611A)

    # le 33611A a enlever
    p5000a.write(r'MMEM:LOAD:FILE "C:\Users\NP700007626\Desktop\routines\states\amplification.csa"')
    amp.operate(srfd_com)
    p5000a.write("OUTP ON")
    p5000a.write("SENSe:SWEep:MODE SINGle")
    wait_for_single(p5000a)
    s21_raw = p5000a.query("CALC:MEAS1:DATA:FDATa?")
    p5000a.write("OUTP OFF")
    amp.standby(srfd_com)
    swg.off(swg33522B, swg33611A)
    s21_mag = 20 * numpy.log10(numpy.abs(parse_data(s21_raw)))
    s21_phase = numpy.degrees(numpy.angle(parse_data(s21_raw)))
    in_dbm = numpy.linspace(-60, 0, 241)
    with open("C:\\Users\\NP700007626\\Downloads\\amplification.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['input power (dBm)','output power (dBm)', 'output phase (deg)'])
        for c1, c2, c3 in zip(in_dbm, s21_mag, s21_phase):
            writer.writerow([c1, c2, c3])
    print("amplification fidelity data saved in download (amplification.csv)")

    #visualisation to add dans l ihm
    matplotlib.pyplot.figure("gain linearity")
    matplotlib.pyplot.plot(in_dbm, s21_mag)
    matplotlib.pyplot.figure("phase linearity")
    matplotlib.pyplot.plot(in_dbm, s21_phase)
    return
    
def interpulse_stability (p5000a, srfd_com, swg33522B, swg33611A, mxo3):
    print()
    print("Starting interpulse stability measure")
    amp.standby(srfd_com)
    amp.body_mode(srfd_com)
    swg.config_vna(swg33522B)
    mxo.config_vna(mxo3)
    swg.on(swg33522B, swg33611A)
    p5000a.write(r'MMEM:LOAD:FILE "C:\Users\NP700007626\Desktop\routines\states\inter_pulse_stability.csa"')
    amp.operate(srfd_com)
    p5000a.write("OUTP ON")
    p5000a.write("SENSe:SWEep:MODE SINGle")
    wait_for_single(p5000a)
    s21_raw = p5000a.query("CALC:MEAS1:DATA:FDATa?")
    p5000a.write("OUTP OFF")
    amp.standby(srfd_com)
    swg.off(swg33522B, swg33611A)
    s21_mag = 20 * numpy.log10(numpy.abs(parse_data(s21_raw)))
    s21_phase = numpy.degrees(numpy.angle(parse_data(s21_raw)))
    matplotlib.pyplot.figure("interpulse gain stability")
    matplotlib.pyplot.plot(s21_mag)
    matplotlib.pyplot.figure("interpulse phase stability")
    matplotlib.pyplot.plot(s21_phase)
    gain_stability = numpy.max(s21_mag) - numpy.min(s21_mag)
    phase_stability = numpy.max(s21_phase) - numpy.min(s21_phase)
    return gain_stability, phase_stability