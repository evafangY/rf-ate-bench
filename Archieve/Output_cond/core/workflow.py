from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from Output_cond.ui.login_page import LoginPage
from Output_cond.ui.transition_page import TransitionPage
from Output_cond.ui.step_page import Step
from Output_cond.ui.measure_body_page import MeasureBodyPage
from Output_cond.ui.measure_head_page import MeasureHeadPage
from Output_cond.core.visa_setup import connect_instruments


class MainWindow(QWidget):
    def __init__(self, rm, scope, swg33611A, com_status):
        super().__init__()

        self.setWindowTitle("Workflow SRFD II")
        self.resize(900, 700)

        # --- VISA instruments ---
        self.rm = rm
        self.scope = scope
        self.swg = swg33611A
        self.com_status = com_status

        if com_status is True:
            print("Communication OK du premier coup")
        elif com_status is False:
            print("⚠️ Première tentative échouée → Reconnexion réussie")
        else:
            print("❌ Communication impossible avec les instruments")

        # --- User info + results ---
        self.user_info = {}
        self.body_results = None
       # self.output_list = {}

        # --- Stack ---
        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # --- Pages ---
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
                "On va commencer le process du Tune Output",
                self.next_step,
                first=True
            )
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
        self.add_step("Câblage - Étape 5 : Connexion entre les instruments & le module combiner", "Combiner_connection.png")
        self.add_step("Câblage - Étape 6 : Connecter le module à l'oscilloscope - Mode Body", "Oscilloscope_Body.png")

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
                "Partie 4 : Mesure BODY",
                self.next_step,
                image_path="MesureBody.png"
            )
        )

        self.add_step("Mesure - Étape : Connecter le module à l'oscilloscope - Mode Head", "Oscilloscope_Body.png")

        self.stack.addWidget(
            MeasureBodyPage(
                self.scope,
                self.swg,
                self.next_step
            )
        )

        # PARTIE 5 — MESURE HEAD
        self.stack.addWidget(
            TransitionPage(
                "Partie 5 : Câblage pour HEAD",
                self.next_step,
                image_path="MesureHead.png"
            )
        )

        self.add_step("Câblage - Étape 8 : Connecter le module à l'oscilloscope - Mode Head", "Oscilloscope_Head.png")

        self.stack.addWidget(
            MeasureHeadPage(
                self.scope,
                self.swg,
                self.next_step
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
