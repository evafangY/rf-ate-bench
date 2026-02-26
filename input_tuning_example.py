from ATE_Lib_AN8103.ate_lib import ate_init
from ATE_Lib_AN8103.ate_lib import COMM_Error
from ATE_Lib_AN8103.ate_lib import ATE_Instrument_Error

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    """ ATE initialization """
    ate = ate_init()
    
    """ high level test launch """
    
    input1, input2 = ate.input_tuning("body", "0")
    print("input1:", round(input1, 3), "input2:", round(input2, 3))
    while not(0.133 < input1 < 0.137) and not(0.133 < input2 < 0.137):
        input("Tune the body gain until the scope measure 135mV RMS, then press enter...")
        input1, input2 = ate.input_tuning("body", "0")
        print("input1:", round(input1, 3), "input2:", round(input2, 3))
    
    
    input1, input2 = ate.input_tuning("head", "0")
    print("input1:", round(input1, 3), "input2:", round(input2, 3))
    while not(0.045 < input1 < 0.049) and not(0.045 < input2 < 0.049):
        input("Tune the head gain until the scope measure 47mV RMS, then press enter...")
        input1, input2 = ate.input_tuning("head", "0")
        print("input1:", round(input1, 3), "input2:", round(input2, 3))
    
    ate.poweroff()
    
    
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