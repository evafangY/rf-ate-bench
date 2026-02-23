from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from Input_cond.ui.login_page import LoginPage
from Input_cond.ui.step_page import Step
from Input_cond.ui.transition_page import TransitionPage
from Input_cond.core.measure_pages import MeasureBodyPage, MeasureHeadPage
from Input_cond.core.visa_setup import connect_instruments


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Workflow Input Gain")
        self.resize(900, 700)

        # Instruments VISA
        scope, swg33522B, swg33611A, srfd_com, com_status = connect_instruments()

        if com_status is True:
            print("Communication OK du premier coup")
        elif com_status is False:
            print("⚠️ Première tentative échouée → Reconnexion réussie")
        else:
            print("❌ Communication impossible avec les instruments")

        self.scope = scope
        self.swg33522B = swg33522B
        self.swg33611A = swg33611A
        self.srfd_com = srfd_com

        # Données utilisateur + résultats BODY
        self.user_info = {}
        self.body_results = None

        # Stack
        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Construction du workflow
        self.build_workflow()

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)

    # ---------------------------------------------------------
    # BUILD WORKFLOW
    # ---------------------------------------------------------
    def build_workflow(self):

        # LOGIN
        self.stack.addWidget(LoginPage(self.next_step))

        # INTRO
        self.stack.addWidget(
            TransitionPage(
                "On va commencer le process du Input Tunning de l'amplificateur 1.5T - Banc 3 - ",
                self.next_step,
                first=True
            )
        )

        # AVERTISSEMENT
        self.add_step(
            "AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V",
            "Cabinet_alim.png",
            security=True
        )

        # PARTIE 1 — IDENTIFICATION
        self.stack.addWidget(
            TransitionPage(
                "Partie 1 du process :\nIdentification du matériel",
                self.next_step,
                image_path="IDN.png"
            )
        )

        self.add_step("Identification matériel - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Identification matériel - Étape 2 : Identifier l'amplificateur avant de l'utiliser / l'installer", "Amplifier.png")
        self.add_step("Identification matériel - Étape 3 : Identifier les instruments de mesures à piloter", "Materials.png")

        # PARTIE 2 — CÂBLAGE
        self.stack.addWidget(
            TransitionPage(
                "Partie 2 du process :\nCâblage",
                self.next_step,
                image_path="Cablage.png"
            )
        )

        self.add_step("Câblage - Étape 1 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage - Étape 2 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage - Étape 3 : Fermé VS Ouvert", "Amplifier_O&C.png")
        self.add_step("Câblage - Étape 4 : Identifier le module", "Combiner_Module.png")
        self.add_step("Câblage - Étape 5 : Brancher l'amplificateur au boitier de communication", "COM.png")
        self.add_step("Câblage - Étape 6 : Connecter les instruments à l'ordinateur", "USB.png")

        # PARTIE 3 — MISE EN MARCHE
        self.stack.addWidget(
            TransitionPage(
                "Partie 3 du process :\nMise en marche",
                self.next_step,
                image_path="Mise_en_marche.png"
            )
        )

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        # PARTIE 4 — MESURE BODY
        self.stack.addWidget(
            TransitionPage(
                "Partie 4 : Mesure Body",
                self.next_step,
                image_path="MesureBody.png"
            )
        )

        self.add_step("Body Mode : Effectuer le câblage suivant pour le mode Body", "Body_cablage.png")

        self.stack.addWidget(
            MeasureBodyPage(
                self.scope,
                self.swg33522B,
                self.swg33611A,
                self.srfd_com,
                self.next_step
            )
        )

        # PARTIE 5 — MESURE HEAD
        self.stack.addWidget(
            TransitionPage(
                "Partie 5 : Mesure Head",
                self.next_step,
                image_path="MesureHead.png"
            )
        )

        self.add_step("Head Mode : Effectuer le câblage suivant pour le mode Head", "Head_cablage.png")

        self.stack.addWidget(
            MeasureHeadPage(
                self.scope,
                self.swg33522B,
                self.swg33611A,
                self.srfd_com
            )
        )

    # ---------------------------------------------------------
    # STEP MANAGEMENT
    # ---------------------------------------------------------
    def add_step(self, titre, image, security=False, first_step=False):
        step = Step(titre, image, self.next_step, self.prev_step, security, first_step)
        self.stack.addWidget(step)

    def next_step(self):
        self.current_index += 1
        if self.current_index < self.stack.count():
            self.stack.setCurrentIndex(self.current_index)

    def prev_step(self):
        self.current_index -= 1
        if self.current_index >= 0:
            self.stack.setCurrentIndex(self.current_index)
