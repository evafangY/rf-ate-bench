PERFORMANCE_SPECS = {
    "12007": ("Input VSWR < 1.5:1", "-", None, 1.50),
    "13101": ("Body Bandwidth (±275kHz)", "dB", 0.00, 0.40),
    "13102": ("Head Bandwidth (±275kHz)", "dB", 0.00, 0.40),
    "13103": ("Body output power nominal", "dBm", 72.04, None),
    "13104": ("Head output power nominal", "dBm", 63.00, None),
    "13105": ("Body output margin (fault peak - nominal peak)", "dB", None, 1.50),
    "13106": ("Body gain (output-input)", "dB", 71.54, 72.54),
    "13107": ("Head delta gain", "dB", 62.44, 63.64),
    "13108": ("Seq1 body output power variation", "%", None, 2.00),
    "13109": ("Seq2 body output power variation", "%", None, 2.00),
    "13110": ("Seq3 body output power variation", "%", None, 2.00),
    "13111": ("Seq4 body output power variation", "%", None, 2.00),
    "13112": ("Seq5 body output power variation", "%", None, 2.00),
    "13113": ("Seq6 body output power variation", "%", None, 2.00),
    "13114": ("Seq7 body output power variation", "%", None, 2.00),
    "13115": ("Seq8 body output power variation", "%", None, 2.00),
    "13201": ("Harmonic output", "dBc", None, -30.00),
    "13204": ("Ublanked output noise power broad spectrum", "dBm/Hz", None, -70.00),
    "13205": ("Gain non-linearity, body forward (-40 to 0 dBm)", "dB", 0.00, 0.80),
    "13206": ("Differential gain, body forward (-40 to -3 dBm)", "dB/dB", -0.10, 0.10),
    "13207": ("Differential gain, body forward (-3 to -1 dBm)", "dB/dB", -0.20, 0.10),
    "13208": ("Differential gain, body forward (-1 to 0 dBm)", "dB/dB", -0.30, 0.10),
    "13209": ("Phase non-linearity, body forward (-40 to 0 dBm)", "deg", 0.00, 6.00),
    "13210": ("Differential phase, body forward (-40 to -3 dBm)", "deg/dB", -0.50, 0.50),
    "13211": ("Differential phase, body forward (-3 to -1 dBm)", "deg/dB", -1.75, 0.50),
    "13212": ("Differential phase, body forward (-1 to 0 dBm)", "deg/dB", -3.00, 0.50),
    "13213": ("Gain non-linearity, body reverse (-40 to 0 dBm)", "dB", 0.00, 0.80),
    "13214": ("Differential gain, body reverse (-40 to -3 dBm)", "dB/dB", -0.10, 0.10),
    "13215": ("Differential gain, body reverse (-3 to -1 dBm)", "dB/dB", -0.20, 0.10),
    "13216": ("Differential gain, body reverse (-1 to 0 dBm)", "dB/dB", -0.30, 0.10),
    "13217": ("Phase non-linearity, body reverse (-40 to 0 dBm)", "deg", 0.00, 6.00),
    "13218": ("Differential phase, body reverse (-40 to -3 dBm)", "deg/dB", -0.50, 0.50),
    "13219": ("Differential phase, body reverse (-3 to -1 dBm)", "deg/dB", -1.75, 0.50),
    "13220": ("Differential phase, body reverse (-1 to 0 dBm)", "deg/dB", -3.00, 0.50),
    "13301": ("Body gain magnitude variation", "dB", 0.00, 0.35),
    "13302": ("Magnitude – body 1 (low average power)", "dB", 0.00, 0.09),
    "13303": ("Phase – body 1 (low average power)", "deg", 0.00, 1.50),
}


OUTPUT_COND_SPECS = {
    "14001": ("Head/Body RF port isolation", "dB", 30.00, None),
    "14002": ("Body RF sample outputs A gain", "dB", -51.00, -49.00),
    "14003": ("Body RF sample outputs B gain", "dB", -51.00, -49.00),
    "14004": ("Head RF sample outputs A gain", "dB", -41.00, -39.00),
    "14005": ("Head RF sample outputs B gain", "dB", -41.00, -39.00),
    "14011": ("TR input/RF output port isolation", "dB", 35.00, None),
    "14009": ("Head TR resistance to head output", "ohm", 0.00, 0.10),
    "14010": ("Body TR resistance to body output", "ohm", 0.00, 0.10),
}


INPUT_COND_SPECS = {
    "12001": ("Body RF port -4 dBm, adjust gain to get body PEP", "dBm", 72.04, None),
    "12002": ("Body RF port -4 dBm, adjust gain to get head PEP", "dBm", 61.04, 65.04),
    "12003": ("Body RF port 10 dBm, adjust gain to get body PEP", "dBm", 72.04, None),
    "12004": ("Body RF port 10 dBm, adjust gain to get head PEP", "dBm", 61.04, 65.04),
    "12005": ("Body RF port 3.5 dBm, adjust gain to get body PEP", "dBm", 72.04, None),
    "12006": ("Head RF port 3.5 dBm, adjust gain to get head PEP", "dBm", 61.04, 65.04),
}


NOISE_SPECS = {
    "13202": ("Coherent noise (narrow spectrum)", "dBm", None, -143.00),
    "13203": ("Random noise (broad spectrum)", "dBm/Hz", None, -160.00),
}

DIAGNOSTIC_SPECS = {
    "bias": ("Bias nominal", "", 175, 225),
}

DIAGNOSTIC_EXCLUDED_BIASES = ["biasQ31", "biasQ33", "biasQ35"]
