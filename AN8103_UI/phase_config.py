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
    "CONF_BASIC": {
        "title": "ATE 01 Configurtion Basique",
        "image": "Models/Pics/ATE_01.png",
        "instruction": (
            "Utiliser la configuration ATE 01 – configuration de base.\n"
            "Vérifier que l’alimentation triphasée est connectée et que les câbles de communication  et les câbles de sorties sont correctement raccordés comme suit :\n"
            "- Main COMM J18 de l’amplificateur → Main COMM de l’ATE \n"
            "- Master COMM de l’amplificateur → Master COMM de l’ATE\n"
            "- Slave COMM de l’amplificateur → Slave COMM de l’ATE\n"
            "- RF IN J14 de l’amplificateur → Sortie RF de l’ATE\n"
            "- BODY RF OUT de l’amplificateur → Charge BODY de l’ATE\n"
            "- HEAD RF OUT de l’amplificateur → Charge HEAD de l’ATE\n"
        ),
    },

    "CONF_OUTPUTCOND": {
        "title": "Montage A : Réglage du module de sortie (ATE02)",
        "image": "Models/Pics/configuration_A.png",
        "instruction": (
            "Utiliser la configuration ATE 02 – configuration pour le réglage de la sortie conditionnelle.\n"
            "Un oscilloscope 8 voies est requis."
        ),
    },
    
    "CONF_INPUTCOND": {
        "title": "Montage B : Réglage du module d'entrée",
        "image": "Models/Pics/configuration_B.png",
        "instruction": (
            "Utiliser la configuration ATE 01 – configuration de base.\n"
            "Déconnecter les câbles de sortie du module de conditionnement d’entrée et les connecter aux voies 3 et 4 de l’oscilloscope.\n"
        ),
    },
    "CONF_SW_TUNING": {
        "title": "Montage C : Réglage du gain des modules de puissance par logiciel",
        "image": "Models/Pics/configuration_C.png",
        "instruction": (
            "Utiliser la configuration ATE 01 – configuration de base.\n"
            "Déconnecter les câbles de sortie des modules de puissance.\n"
            "Connecter:\n"
            "- Sortie du module Master → Charge BODY \n"
            "- Sortie du module Slave → Charge HEAD \n"   
        ),
    },
    "CONF_PERF": {
        "title": "Montage D : Test de performance / Burn",
        "image": "Models/Pics/configuration_D.png",
        "instruction": (
            " Utiliser la configuration ATE 01 – configuration de base.\n"
            "Ajouter un puissance mètre à la sortie BODY RF OUT."
        ),
    },
    "CONF_NOISE": {
        "title": "Montage E : Mesure de bruit",
        "image": "Models/Pics/configuration_E.png",
        "instruction": (
            "Utiliser la configuration ATE 01 – configuration de base.\n"
            "Déconnecter le câble de sortie BODY RF OUT et connecter le LNA ainsi que son alimentation.\n\n"
            "/!\\ ATTENTION /!\\\n"
            "Seul le test de bruit en mode blanked peut être réalisé dans cette configuration.\n"
            "Tout autre test peut entraîner un risque d’endommagement du matériel."
        ),    
    },
}


PHASE_CONFIG = {
    "Diagnostic": {
        "display_name": "Diagnostic",
        "ate_config": "CONF_BASIC",
        "image": "Models/Pics/ATE_01.png",
        "instruction": (
            "Le diagnostic va lire l'état et les registres d'erreur."
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 01. Configuration basique.\n Cliquer sur 'Vérifié' pour continuer.",
        "caption": "",
    },
    "Output conditional tuning": {
        "display_name": "Réglage du module de sortie",
        "ate_config": "CONF_OUTPUTCOND",
        "image": "Models/Pics/reglage_output.png",
        "instruction": (
            "La carte de sortie sera réglée pendant cet étape.\n"
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 02. Vérifier que les câbles de sont connectés correctement.",
        "caption": "",
        "enable_subtests_on_run": True,
        "subtests": [
            {"method": "run_step2_oscilloscope_tests", "label": "Mesures Oscilloscope (8 ch)"},
            {"method": "run_step2_resistance_head", "label": "Résistance Head"},
            {"method": "run_step2_resistance_body", "label": "Résistance Body"},
        ],
    },
    "Input conditional board tuning": {
        "display_name": "Réglage du module d'entrée",
        "ate_config": "CONF_INPUTCOND",
        "image": "Models/Pics/reglage_gain.png",
        "instruction": (
            "La carte d'entrée sera réglée pendant cet étape.\n"
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 01. Configuration B.\n Les sorties de la carte d'entrée doivent être connectées aux voies 3 et 4 de l'oscilloscope.",
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
        "image": "Models/Pics/ATE_01.png",
        "instruction": (
            "Les modules de puissance seront réglées pendant cet étape.\n"
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 01. Configuration D. \n La sortie de Master module doit être connectée à la charge BODY.\n La sortie de Slave module doit être connectée à la charge HEAD.",
        "caption": "",
    },
    
    "Performance test / burn": {
        "display_name": "Test de performance / Burn",
        "ate_config": "CONF_PERF",
        "image": "Models/Pics/ATE_01.png",
        "instruction": (
            "Les tests de performance seront réalisés pendant cet étape.\n"
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 01. Configuration D.\n La puissance metre doit être connecté à la sortie de BODY.",
        "caption": "",
        "enable_subtests_on_run": True,
        "execute_all_subtests": True,
        "subtests": [
            {"method": "single_pulse_measure", "label": "Mesure single pulse"},
            {"method": "harmonic_output_measure", "label": "Mesure harmonique"},
            {"method": "noise_unblanked_measure", "label": "Mesure bruit blanké"},
            {"method": "interpulse_stability_measure", "label": "Mesure stabilité inter-pulse"},
            {"method": "gain_flatness_measure", "label": "Mesure gain flatness"},
            {"method": "fidelity_measure", "label": "Mesure fidélité"},
            {"method": "run_stress_1", "label": "Stress 1"},
            {"method": "run_stress_2", "label": "Stress 2"},
            {"method": "run_stress_3", "label": "Stress 3"},
            {"method": "run_stress_4", "label": "Stress 4"},
            {"method": "run_stress_5", "label": "Stress 5"},
            {"method": "run_stress_6", "label": "Stress Burst 6"},
            {"method": "run_stress_7", "label": "Stress Burst 7"},
            {"method": "run_stress_8", "label": "Stress Burst 8"},
        ],
    },
    "Factory gain reset": {
        "display_name": "Réglage d'usine",
        "ate_config": "CONF_PERF",
        "image": "Models/Pics/reglage_gain.png",
        "instruction": (
            "Le réglage d'usine sera réalisé pendant cet étape. RF in à 3.5dBm @PEP\n"
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 01. Configuration D.\n La puissance metre doit être connecté à la sortie de BODY.",
        "caption": "",
        "enable_subtests_on_run": True,
        "locked_subtests": ["Réglage final BODY", "Réglage final HEAD"],
        "unlock_when_subtests_done": ["Pré-réglage BODY"],
        "subtests": [
            {"method": "run_factory_gain_pre_body", "label": "Pré-réglage BODY"},
            {"method": "run_factory_gain_body_final", "label": "Réglage final BODY"},
            {"method": "run_factory_gain_head_final", "label": "Réglage final HEAD"}
        ],
    },
    "Noise blanked": {
        "display_name": "Mesure de bruit blanké",
        "ate_config": "CONF_NOISE",
        "image": "Models/Pics/ATE_01.png",
        "instruction": (
            "La mesure de bruit blanké sera réalisée pendant cet étape.\n"
        ),
        "require_check": True,
        "check_text": "Vérifier que vous travaillez sur ATE 01. Configuration E.\n La sortie de BODY doit être connectée directement sur le LNA.",
        "caption": "",
    },
}
