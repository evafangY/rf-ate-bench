import time
import math

def scope_output_cond_setup(scope, mode="Body"):
    scope.write("*RST")
    scope.write("CHANnel1:COUPling DC")
    scope.write("CHANnel2:COUPling DC")
    scope.write("CHANnel3:COUPling DC")
    scope.write("CHANnel4:COUPling DC")
    scope.write("TRIGger:MODE NORMal")
    scope.write("CHANnel1:BANDwidth 350E6")
    scope.write("CHANnel2:BANDwidth 350E6")
    scope.write("CHANnel3:BANDwidth 350E6")
    scope.write("CHANnel4:BANDwidth 350E6")
    scope.write("TRIGger:EVENt1:SOURce EXTernanalog")
    scope.write("TRIGger:ANEDge:LEVel 0.8")
    scope.write("TRIGger:ANEDge:COUPling DC")
    scope.write("TIMebase:SCALe 1E-8")
    scope.write("CHANnel1:SCALe 1")
    scope.write("CHANnel3:SCALe 0.001")
    scope.write("CHANnel1:STATe ON")
    scope.write("CHANnel2:STATe ON")
    scope.write("CHANnel3:STATe ON")
    scope.write("CHANnel4:STATe ON")
    scope.write("MEASurement1:MAIN CYCRms")
    scope.write("MEASurement1:SOURce C1")
    scope.write("MEASurement2:MAIN CYCRms")
    scope.write("MEASurement2:SOURce C2")
    scope.write("MEASurement3:MAIN CYCRms")
    scope.write("MEASurement3:SOURce C3")
    scope.write("MEASurement4:MAIN CYCRms")
    scope.write("MEASurement4:SOURce C4")
    scope.write("ACQuire:TYPE AVERage")
    scope.write("ACQuire:COUNt 100")
    scope.query("*OPC?")

    if mode == "Body":
        scope.write("CHANnel2:SCALe 0.004")
        scope.write("CHANnel4:SCALe 0.004")
    else:
        scope.write("CHANnel2:SCALe 0.010")
        scope.write("CHANnel4:SCALe 0.010")


def swg_output_cond_setup(swg):
    swg.write("*RST")
    swg.write("OUTPut1:LOAD 50")
    swg.write("SOURce1:FUNCtion SIN")
    swg.write("SOURCE1:FREQUENCY 63860000")
    swg.write("SOURCE1:VOLT:UNIT DBM")
    swg.write("SOURCE1:VOLT 22")
    swg.write("OUTPUT1 ON")
    swg.query("*OPC?")


def configure(scope, swg, mode="Body"):
    swg_output_cond_setup(swg)
    scope_output_cond_setup(scope, mode)
    time.sleep(1)
