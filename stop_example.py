from ATE_Lib_AN8103.ate_lib import ate_init
from ATE_Lib_AN8103.ate_lib import COMM_Error
from ATE_Lib_AN8103.ate_lib import ATE_Instrument_Error

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    """ ATE initialization """
    ate = ate_init()
    
    ate.sw.config("vna_body")
    
    """ high level stop """
    # ate.poweroff()
    
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