from ate_lib_AN8103.ate_lib import ate_init
from ate_lib_AN8103.ate_lib import COMM_Error
from ate_lib_AN8103.ate_lib import ATE_Instrument_Error

import logging
import matplotlib.pyplot


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    """ ATE initialization """
    ate = ate_init()
    
    """ high level test launch """
    ate.performance_test()
    
    # """ reading test results """
    # test_id_13301 = ate.test_id_13301
    # test_id_13201 = ate.test_id_13201
    # test_id_13204 = ate.test_id_13204
    # matplotlib.pyplot.figure("interpulse gain stability")
    # matplotlib.pyplot.plot(ate.interpulse_s21_mag)
    # matplotlib.pyplot.figure("interpulse phase stability")
    # matplotlib.pyplot.plot(ate.interpulse_s21_phase)
    # matplotlib.pyplot.figure("s11")
    # matplotlib.pyplot.plot(ate.flatness_s11_mag)
    # matplotlib.pyplot.figure("gain flatness body")
    # matplotlib.pyplot.plot(ate.flatness_s21_mag_body)
    matplotlib.pyplot.figure("stress 1")
    matplotlib.pyplot.plot(ate.stress_1_mag)
    matplotlib.pyplot.figure("stress 2")
    matplotlib.pyplot.plot(ate.stress_2_mag)
    matplotlib.pyplot.show()
    
    # """ printing result in terminal """
    # print("")
    # print("MAIN:")
    # print("\033[36mSingle pulse drop (13301):", round(test_id_13301, 2), "dB\033[0m")
    # print("\033[36mHarmonic output (13201):  ", round(test_id_13201, 2), "dB\033[0m")
    # print("\033[36mNoise unblanked (13204):  ", round(test_id_13204, 2), "dBm/Hz\033[0m")
    
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