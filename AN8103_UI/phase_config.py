PHASES = [
    "Diagnostic",
    "Output conditional tuning",
    "Input conditional board tuning",
    "Power module gain tuning",
    "Performance test / burn",
    "Factory gain reset",
    "Noise blanked",
]


ATE_CONFIGURATIONS = {
    "CONF_OUTPUTCOND": {
        "title": "Montage A : Réglage du module de sortie (ATE02)",
        "image": "Models/Pics/Master_Slave_Connection.png",
        "instruction": (
            "Préparer le montage pour le réglage de la sortie conditionnelle.\n"
            "Connecter l'alimentation et les câbles de communication pour le diagnostic."
        ),
    },
    
    "CONF_INPUTCOND": {
        "title": "Montage B : Réglage du module d'entrée",
        "image": "Models/Pics/Input_Conditional_Tuning.png",
        "instruction": (
            "Préparer le montage pour régler et vérifier la plage d'entrée.\n"
            "Déconnecter les deux sorties du module d'entrée (Jxx et Jxx).\n"
            "Connecter ces deux sorties à l'oscilloscope."

        ),
    },
    "CONF_SW_TUNING": {
        "title": "Montage C : Réglage du gain des modules de puissance par logiciel",
        "image": "Models/Pics/Power_module_tunning.png",
        "instruction": (
            "Préparer le montage pour le réglage des modules de puissance.\n"
            "Connecter la charge BODY à la sortie du module Master, la charge HEAD à la sortie du module Slave."
        ),
    },
    "CONF_PERF": {
        "title": "Montage D : Test de performance / Burn",
        "image": "Models/Pics/Master_Slave_Connection.png",
        "instruction": (
            "Préparer le montage pour les tests.\n"
            "Connecter la charge BODY à la sortie BODY, la charge HEAD à la sortie HEAD de l'amplificateur."
        ),
    },
    "CONF_NOISE": {
        "title": "Montage E : Mesure de bruit",
        "image": "Noise_meas/Pics/Noise.jpg",
        "instruction": (
            "Préparer le montage pour la mesure de bruit.\n"
            "La sortie de BODY est connectée directement sur le LNA.\n\n"
            "/!\\ ATTENTION /!\\\n"
            "Seuls les tests de bruit peuvent être exécutés pendant cette phase."
        ),
    },
}


PHASE_CONFIG = {
    "Diagnostic": {
        "display_name": "Diagnostic",
        "ate_config": "CONF_PERF",
        "image": "Models/Pics/Master_Slave_Connection.png",
        "instruction": (
            "1. Connecter l'alimentation de l'amplificateur au banc.\n"
            "2. Connecter les câbles de communication (Main, Master, Slave).\n"
            "3. Alimenter l'amplificateur.\n\n"
            "Le diagnostic va lire l'état et les registres d'erreur."
        ),
        "require_check": True,
        "check_text": "Vérifier toutes les connexions (Alimentation + Communication).\nCliquer sur 'Vérifié' pour continuer.",
        "caption": "",
    },
    "Output conditional tuning": {
        "display_name": "Réglage du module de sortie",
        "ate_config": "CONF_OUTPUTCOND",
        "image": "Models/Pics/Output_Conditional_Tuning_Connection.png",
        "instruction": (
            "Préparer le réglage de la sortie conditionnelle (Output Conditional Tuning).\n"
            "Assurez-vous que la configuration est correcte."
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 02. Vérifier que les câbles de sont connectés correctement.",
        "caption": "",
    },
    "Input conditional board tuning": {
        "display_name": "Réglage du module d'entrée",
        "ate_config": "CONF_INPUTCOND",
        "image": "Models/Pics/Input_Conditional_Tuning_Connection.png",
        "instruction": (
            "Préparer le réglage du module d'entrée (Input Conditional Tuning).\n"
            "Assurez-vous que la configuration est correcte."
        ),
        "require_check": True,
        "check_text": "Vérifier que les câbles de sortie du module d'entrée sont connectés à l'oscilloscope.",
        "caption": "",
        "enable_subtests_on_run": True,
        "locked_subtests": ["Body 0dBm", "Head 0dBm"],
        "unlock_when_subtests_done": ["Body -4dBm", "Head -4dBm", "Body +10dBm", "Head +10dBm"],
        "subtests": [
            {"method": "run_input_tuning_step_1", "label": "Body -4dBm"},
            {"method": "run_input_tuning_step_2", "label": "Head -4dBm"},
            {"method": "run_input_tuning_step_3", "label": "Body +10dBm"},
            {"method": "run_input_tuning_step_4", "label": "Head +10dBm"},
            {"method": "run_input_tuning_step_0dbm_body", "label": "Body 0dBm"},
            {"method": "run_input_tuning_step_0dbm_head", "label": "Head 0dBm"},
        ],
    },
    "Power module gain tuning": {
        "display_name": "Réglage du gain du module de puissance",
        "ate_config": "CONF_SW_TUNING",
        "image": "Models/Pics/Power_module_tunning_connection.png",
        "instruction": (
            "Préparer le réglage du gain des modules de puissance.\n"
            "Vérifier que les charges sont connectées aux sorties."
        ),
        "require_check": True,
        "check_text": "Vérifier que les câbles de puissance sont connectés aux modules de puissance Master et Slave.",
        "caption": "",
    },
    
    "Performance test / burn": {
        "display_name": "Test de performance / Burn",
        "ate_config": "CONF_PERF",
        "image": "Models/Pics/ATE_configuration3.png",
        "instruction": (
            "Réaliser le test de performance RF complet.\n"
            "Vérifier que tous les paramètres respectent les spécifications.\n"
            "Utiliser la photo ci-dessous comme référence."
        ),
        "require_check": True,
        "check_text": "Vérifier que les câbles de puissance sont connectés aux sorties BODY et HEAD.",
        "caption": "",
        "subtests": [
            {"method": "single_pulse_measure", "label": "Mesure single pulse"},
            {"method": "harmonic_output_measure", "label": "Mesure harmonique"},
            {"method": "noise_unblanked_measure", "label": "Mesure bruit blanké"},
        ],
    },
    "Factory gain reset": {
        "display_name": "Réglage d'usine",
        "ate_config": "CONF_PERF",
        "image": "Models/Pics/ATE_configuration3.png",
        "instruction": (
            "Appliquer le réglage d'usine de l'amplificateur.\n"
            "Cette étape prépare l'unité pour la mesure de bruit."
        ),
        "require_check": True,
        "check_text": "Vérifier que les câbles de puissance sont connectés aux sorties BODY et HEAD.",
        "caption": "",
    },
    "Noise blanked": {
        "display_name": "Mesure de bruit blanké",
        "ate_config": "CONF_NOISE",
        "image": "Models/Pics/Blanked_noise_connection.png",
        "instruction": (
            "Mesurer le bruit blanké sur le canal BODY.\n"
            "Suivre strictement les consignes de sécurité pour la mesure de bruit."
        ),
        "require_check": True,
        "check_text": "Vérifier la sortie de BODY est connectée directement sur le LNA.",
        "caption": "",
    },
}
