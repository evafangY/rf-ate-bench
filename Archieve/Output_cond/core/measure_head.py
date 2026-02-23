import math

def measure_head(scope):
    scope.write("MEASurement1:RESult:ACTual?"); J3 = float(scope.read())
    scope.write("MEASurement2:RESult:ACTual?"); J5 = float(scope.read())
    scope.write("MEASurement3:RESult:ACTual?"); J9 = float(scope.read())
    scope.write("MEASurement4:RESult:ACTual?"); J7 = float(scope.read())

    return {
        "J3": J3,
        "J5": round(-20*math.log10(J5/J3),2),
        "J7": round(-20*math.log10(J7/J3),2),
        "J9": round(-20*math.log10(J9/J3),2)
    }
