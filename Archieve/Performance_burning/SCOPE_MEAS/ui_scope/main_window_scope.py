import pyvisa
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtGui import QColor

from Performance_burning.SCOPE_MEAS.ui_scope.login_page_scope import LoginPageScope
from Performance_burning.SCOPE_MEAS.ui_scope.step_page_scope import StepScope
from Performance_burning.SCOPE_MEAS.ui_scope.transition_page_scope import TransitionPageScope
from Performance_burning.SCOPE_MEAS.ui_scope.measure_page_scope import MeasurePageScope
from Performance_burning.SCOPE_MEAS.core_scope.visa_setup_scope import Connect_instruments_scope


class MainWindowScope(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow SCOPE – Tests RF")
        self.resize(900, 700)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("white"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.stack = QStackedWidget()
        self.user_info = {}
        self.stack.addWidget(LoginPageScope(self.next_step))

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)


        self.scope, self.swg33522B, self.swg33611A, self.srfd_com, com_status = Connect_instruments_scope()

        if com_status is True:
            print("Communication OK du premier coup")
        elif com_status is False:
            print("⚠️ Première tentative échouée → Reconnexion réussie")
        else:
            print("❌ Communication impossible avec les instruments")


        self.current_index = 0

        self.stack.addWidget(TransitionPageScope("Début du process SCOPE", self.next_step, first=True))
        self.add_step("Avertissement : tension présente en haut du banc", "Cabinet_alim.png", security=True)
        self.stack.addWidget(TransitionPageScope("Partie 1 : Identification matériel", self.next_step, image_path="IDN.png"))

        self.add_step("Étape 1 : Vérification de l'unité d'alimentation", "PDU.png")
        self.add_step("Étape 2 : Identifier l'amplificateur", "Amplifier.png")
        self.add_step("Étape 3 : Identifier les instruments", "Materials_Scope.png")

        self.stack.addWidget(TransitionPageScope("Partie 2 : Câblage", self.next_step, image_path="Cablage.png"))

        self.add_step("Étape 1 : Prendre un tournevis isolant", "Tournevice.png")
        self.add_step("Étape 2 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Étape 3 : Fermé VS Ouvert", "Amplifier_O&C.png")
        self.add_step("Étape 4 : Identifier le module", "Combiner_Module.png")
        self.add_step("Étape 5 : Brancher l'amplificateur au boitier de communication", "COM.png")
        self.add_step("Étape 6 : Connecter le SCOPE & 33500B à l'ordinateur", "USB.png")
        self.add_step("Étape 7 : Effectuer le câblage suivant", "Scope_Cablage_Body.png")

        # Transition vers la partie Alimentation
        self.stack.addWidget(TransitionPageScope(
            "Partie 3 du process : Mise en marche",
            self.next_step,
            image_path="Mise_en_marche.png"
        ))

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        # Transition vers la partie Mesure
        self.stack.addWidget(TransitionPageScope(
            "Partie 4 du process : Commençons la partie mesure",
            self.next_step,
            image_path="Mesure.png"
        ))

        # Page de mesure
        self.stack.addWidget(MeasurePageScope(
            self.scope,
            self.swg33522B,
            self.swg33611A,
            self.srfd_com
        ))

        self.stack.setCurrentIndex(self.current_index)

    def add_step(self, titre, image, security=False):
        self.stack.addWidget(
            StepScope(
                titre,
                image,
                self.next_step,
                self.prev_step,
                security
            )
        )

    def next_step(self):
        self.current_index += 1
        if self.current_index < self.stack.count():
            self.stack.setCurrentIndex(self.current_index)

    def prev_step(self):
        self.current_index -= 1
        if self.current_index >= 0:
            self.stack.setCurrentIndex(self.current_index)
