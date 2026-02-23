import math

def measure_body(scope):
    scope.write("MEASurement1:RESult:ACTual?"); J4 = float(scope.read())
    scope.write("MEASurement2:RESult:ACTual?"); J6 = float(scope.read())
    scope.write("MEASurement3:RESult:ACTual?"); J10 = float(scope.read())
    scope.write("MEASurement4:RESult:ACTual?"); J8 = float(scope.read())

    gJ6 = round(-20*math.log10(J6/J4),2)
    gJ8 = round(-20*math.log10(J8/J4),2)
    gJ10 = round(-20*math.log10(J10/J4),2)

    return {
        "J4": J4,
        "J6": gJ6,
        "J8": gJ8,
        "J10": gJ10
    }
