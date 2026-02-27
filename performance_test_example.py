from ATE_Lib_AN8103.ate_lib import ate_init
from ATE_Lib_AN8103.ate_lib import COMM_Error
from ATE_Lib_AN8103.ate_lib import ATE_Instrument_Error

import logging
import matplotlib.pyplot


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    """ ATE initialization """
    ate = ate_init()
    
    """ high level test launch """
    ate.performance_test()
    
    
    """ reading test results """
    test_id_13301 = ate.test_id_13301
    test_id_13201 = ate.test_id_13201
    test_id_13204 = ate.test_id_13204
    test_id_12007 = ate.test_id_12007
    test_id_13101 = ate.test_id_13101
    test_id_13102 = ate.test_id_13102
    test_id_13106 = ate.test_id_13106
    test_id_13107 = ate.test_id_13107
    test_id_13108 = ate.test_id_13108
    test_id_13109 = ate.test_id_13109
    test_id_13110 = ate.test_id_13110
    test_id_13111 = ate.test_id_13111
    test_id_13112 = ate.test_id_13112
    test_id_13113 = ate.test_id_13113
    test_id_13114 = ate.test_id_13114
    test_id_13115 = ate.test_id_13115
    test_id_13205 = ate.test_id_13205
    test_id_13206 = ate.test_id_13206
    test_id_13207 = ate.test_id_13207
    test_id_13208 = ate.test_id_13208
    test_id_13209 = ate.test_id_13209
    test_id_13210 = ate.test_id_13210
    test_id_13211 = ate.test_id_13211
    test_id_13212 = ate.test_id_13212
    test_id_13213 = ate.test_id_13213
    test_id_13214 = ate.test_id_13214
    test_id_13215 = ate.test_id_13215
    test_id_13216 = ate.test_id_13216
    test_id_13217 = ate.test_id_13217
    test_id_13218 = ate.test_id_13218
    test_id_13219 = ate.test_id_13219
    test_id_13220 = ate.test_id_13220
    test_id_13302 = ate.test_id_13302
    test_id_13303 = ate.test_id_13303
    
    
    """ printing result in terminal """
    print("")
    print("MAIN:")
    print("\033[36mSingle pulse drop (13301):", round(test_id_13301, 2), "dB\033[0m")
    print("\033[36mHarmonic output (13201):  ", round(test_id_13201, 2), "dB\033[0m")
    print("\033[36mNoise unblanked (13204):  ", round(test_id_13204, 2), "dBm/Hz\033[0m")
    print("\033[36mGain inter pulse stability (13302):", round(test_id_13302, 2), "dB\033[0m")
    print("\033[36mPhase inter pulse stability (13303):", round(test_id_13303, 2), "°\033[0m")
    print("\033[36mRF input match (12007):", round(test_id_12007, 2), ":1\033[0m")
    print("\033[36mBody gain flatness (13101):", round(test_id_13101, 2), "dB\033[0m")
    print("\033[36mHead gain flatness (13102):", round(test_id_13102, 2), "dB\033[0m")
    print("\033[36mBody power (13106):", round(test_id_13106, 2), "dBm\033[0m")
    print("\033[36mHead power (13107):", round(test_id_13107, 2), "dBm\033[0m")
    print("\033[36mStress sequence 1 variation (13108):", round(test_id_13108, 2), "%\033[0m")
    print("\033[36mStress sequence 2 variation (13109):", round(test_id_13109, 2), "%\033[0m")
    print("\033[36mStress sequence 3 variation (13110):", round(test_id_13110, 2), "%\033[0m")
    print("\033[36mStress sequence 4 variation (13111):", round(test_id_13111, 2), "%\033[0m")
    print("\033[36mStress sequence 5 variation (13112):", round(test_id_13112, 2), "%\033[0m")
    print("\033[36mStress sequence 6 variation (13113):", round(test_id_13113, 2), "%\033[0m")
    print("\033[36mStress sequence 7 variation (13113):", round(test_id_13114, 2), "%\033[0m")
    print("\033[36mStress sequence 8 variation (13113):", round(test_id_13115, 2), "%\033[0m")
    print("\033[36mFidelity gain non linearity -40 to 0dBm (13205):", round(test_id_13205, 2), "dB\033[0m")
    print("\033[36mFidelity differential gain -40 to -3dBm (13206):", round(test_id_13206, 2), "dB/dB\033[0m")
    print("\033[36mFidelity differential gain -3 to -1dBm (13207):", round(test_id_13207, 2), "dB/dB\033[0m")
    print("\033[36mFidelity differential gain -1 to 0dBm (13208):", round(test_id_13208, 2), "dB/dB\033[0m")
    print("\033[36mFidelity phase non linearity -40 to 0dBm (13209):", round(test_id_13209, 2), "°\033[0m")
    print("\033[36mFidelity differential phase -40 to -3dBm (13210):", round(test_id_13210, 2), "°/dB\033[0m")
    print("\033[36mFidelity differential phase -3 to -1dBm (13211):", round(test_id_13211, 2), "°/dB\033[0m")
    print("\033[36mFidelity differential phase -1 to 0dBm (13212):", round(test_id_13212, 2), "°/dB\033[0m")
    print("\033[36mFidelity gain non linearity 0 to -40dBm (13213):", round(test_id_13213, 2), "dB\033[0m")
    print("\033[36mFidelity differential gain -3 to -40dBm (13214):", round(test_id_13214, 2), "dB/dB\033[0m")
    print("\033[36mFidelity differential gain -1 to -3dBm (13215):", round(test_id_13215, 2), "dB/dB\033[0m")
    print("\033[36mFidelity differential gain 0 to -1dBm (13216):", round(test_id_13216, 2), "dB/dB\033[0m")
    print("\033[36mFidelity phase non linearity 0 to -40dBm (13217):", round(test_id_13217, 2), "°\033[0m")
    print("\033[36mFidelity differential phase -3 to -40dBm (13218):", round(test_id_13218, 2), "°/dB\033[0m")
    print("\033[36mFidelity differential phase -1 to -3dBm (13219):", round(test_id_13219, 2), "°/dB\033[0m")
    print("\033[36mFidelity differential phase 0 to -1dBm (13220):", round(test_id_13220, 2), "°/dB\033[0m")
    
    
    """ plotting vna results """
    matplotlib.pyplot.figure("interpulse gain stability")
    matplotlib.pyplot.plot(ate.interpulse_s21_mag)
    matplotlib.pyplot.figure("interpulse phase stability")
    matplotlib.pyplot.plot(ate.interpulse_s21_phase)
    matplotlib.pyplot.figure("s11")
    matplotlib.pyplot.plot(ate.flatness_s11_mag)
    matplotlib.pyplot.figure("gain flatness body")
    matplotlib.pyplot.plot(ate.flatness_s21_mag_body)
    matplotlib.pyplot.figure("stress 1")
    matplotlib.pyplot.plot(ate.stress_1_mag)
    matplotlib.pyplot.figure("stress 2")
    matplotlib.pyplot.plot(ate.stress_2_mag)
    matplotlib.pyplot.figure("stress 3")
    matplotlib.pyplot.plot(ate.stress_3_mag)
    matplotlib.pyplot.figure("stress 4")
    matplotlib.pyplot.plot(ate.stress_4_mag)
    matplotlib.pyplot.figure("stress 5")
    matplotlib.pyplot.plot(ate.stress_5_mag)
    matplotlib.pyplot.figure("stress 6")
    matplotlib.pyplot.plot(ate.stress_6_mag)
    matplotlib.pyplot.figure("stress 7")
    matplotlib.pyplot.plot(ate.stress_7_mag)
    matplotlib.pyplot.figure("stress 8")
    matplotlib.pyplot.plot(ate.stress_8_mag)
    matplotlib.pyplot.figure("fidelity magnitude forward")
    matplotlib.pyplot.plot(ate.forward_s21_mag)
    matplotlib.pyplot.figure("fidelity magnitude differential forward")
    matplotlib.pyplot.plot(ate.forward_s21_mag_diff)
    matplotlib.pyplot.figure("fidelity phase forward")
    matplotlib.pyplot.plot(ate.forward_s21_phase)
    matplotlib.pyplot.figure("fidelity phase differential forward")
    matplotlib.pyplot.plot(ate.forward_s21_phase_diff)
    matplotlib.pyplot.figure("fidelity magnitude reverse")
    matplotlib.pyplot.plot(ate.reverse_s21_mag)
    matplotlib.pyplot.figure("fidelity magnitude differential reverse")
    matplotlib.pyplot.plot(ate.reverse_s21_mag_diff)
    matplotlib.pyplot.figure("fidelity phase reverse")
    matplotlib.pyplot.plot(ate.reverse_s21_phase)
    matplotlib.pyplot.figure("fidelity phase differential reverse")
    matplotlib.pyplot.plot(ate.reverse_s21_phase_diff)
    matplotlib.pyplot.show()
    
    
#Gestion des erreurs
except COMM_Error as comm_e:
    print("")
    print("Amplifier encountered error", hex(comm_e.code), ", please refer to PSP for diagnostic")
except ATE_Instrument_Error as ate_e:
    print("")
    print("Issue encoutered with", ate_e, " please verify the instrument connections")
except Exception:
    print("")
    print("MAIN:")
    print("Error seen in main")
    print("launching traceback for debug")
    raise