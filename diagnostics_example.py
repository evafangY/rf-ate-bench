from AN8103_lib.ate_lib import ate_init
from AN8103_lib.ate_lib import COMM_Error
from AN8103_lib.ate_lib import ATE_Instrument_Error

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    """ ATE initialization """
    ate = ate_init()
    
    """ diagnostics example """
    ate.diagnostics()
    print()
    print("main:")
    print("amp state:",ate.comm.state)
    
    print("Master amp state :",
    print("master 140V:", ate.master.alim_140)
    print("master 48V:", ate.master.alim_48)
    print("master +15V:", ate.master.alim_p15)
    print("master -15V:", ate.master.alim_m15)
    print("master amp fault:", ate.master.fault)
    
    try: 
        read all bias value and print, if their value is not in 200 +- 25, show the value in red and alarm
 bias list: 
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
 
    try:
        print("master amp Gain:", ate.master.Gai)
    except Exception:
        print("Unable to read standby mode registers")
    
    
    print("slave 140V:", ate.slave.alim_140)
    print("slave 48V:", ate.slave.alim_48)
    print("slave +15V:", ate.slave.alim_p15)
    print("slave -15V:", ate.slave.alim_m15)
    print("slave amp fault:", ate.slave.fault)
       try: 
        read all bias value and print, if their value is not in 200 +- 25, show the value in red and alarm
 bias list: 
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
  
    try:
        print("slave amp Gain:", ate.slave.Gai)
    except Exception:
        print("Unable to read standby mode registers")
    
 
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