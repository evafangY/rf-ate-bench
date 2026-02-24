PHASES = [
    "Diagnostic",
    "Tuning de la sortie conditionnelle",
    "Tuning de la gain du module de puissance",
    "Tuning de l'entrée conditionnelle",
    "Test de performance / burning",
    "Mesure de bruit blanké",
]


PHASE_CONFIG = {
    "Diagnostic": {
        "image": "Models/Pics/Master_Slave_Connection.png",
        "instruction": (
            "Connecter l'alimentation de l'amplificateur au bench.\n"
            "Connecter le cable de communication main, master et slave.\n"
            "Alimenter l'amplificateur.\n"
            "L'outil de diagnostic va lire l'état et les registres d'erreur de l'amplificateur."
        ),
        "require_check": True,
        "check_text": "Vérifier les connections de l'amplificateur et du bench.\nCliquez sur 'Vérifié' une fois vérifié.",
        "caption": "",
    },
    "Tuning de la sortie conditionnelle": {
        "image": "Output_cond/Pics/Amplifier.png",
        "instruction": "",
        "require_check": False,
        "check_text": "",
        "caption": "",
    },
    "Tuning de la gain du module de puissance": {
        "image": "SW_Tunning/Pics/Amplifier.png",
        "instruction": "",
        "require_check": False,
        "check_text": "",
        "caption": "",
    },
    "Tuning de l'entrée conditionnelle": {
        "image": "Input_cond/Pics/Amplifier.png",
        "instruction": "",
        "require_check": False,
        "check_text": "",
        "caption": "",
    },
    "Test de performance / burning": {
        "image": "Models/Pics/ATE_configuration3.png",
        "instruction": (
            "Réaliser un test de performance RF complet et vérifier que tous les paramètres mesurés respectent les spécifications.\n"
            "Utiliser la photo ci-dessous comme référence."
        ),
        "require_check": True,
        "check_text": "Vérifier que la configuration du banc correspond à ATE_configuration3 (configuration 3).\nCliquez sur 'Vérifié' une fois la configuration confirmée.",
        "caption": "Configuration du banc: ATE_configuration3",
        "subtests": [
            {"method": "single_pulse_measure", "label": "Mesure single pulse"},
            {"method": "harmonic_output_measure", "label": "Mesure harmonique"},
            {"method": "noise_unblanked_measure", "label": "Mesure bruit blanké"},
        ],
    },
    "Mesure de bruit blanké": {
        "image": "Noise_meas/Pics/Noise.jpg",
        "instruction": "",
        "require_check": False,
        "check_text": "",
        "caption": "",
    },
}
