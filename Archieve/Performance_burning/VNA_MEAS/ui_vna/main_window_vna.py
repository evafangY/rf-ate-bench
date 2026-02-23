import pyvisa
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from Performance_burning.srfd_lib import amp, vna
from Performance_burning.VNA_MEAS.ui_vna.login_page_vna import LoginPage
from Performance_burning.VNA_MEAS.ui_vna.transition_page_vna import TransitionPage
from Performance_burning.VNA_MEAS.ui_vna.step_page_vna import Step
from Performance_burning.VNA_MEAS.ui_vna.measure_page_vna import MeasurePage
from Performance_burning.VNA_MEAS.core_vna.visa_setup_vna import Connect_instruments_vna


GE_PURPLE = "#4B0082"

class MainWindowVna(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow VNA – Tests RF")
        self.resize(900, 700)
        self.stack = QStackedWidget()
        self.user_info = {}
        self.stack.addWidget(LoginPage(self.next_step))
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)


        self.p5000a, self.swg33522B, self.swg33611A, self.mxo3, self.srfd_com, com_status = Connect_instruments_vna()

        if com_status is True:
            print("Communication OK du premier coup")
        elif com_status is False:
            print("⚠️ Première tentative échouée → Reconnexion réussie")
        else:
            print("❌ Communication impossible avec les instruments")


        # Pages d’intro
        self.stack.addWidget(TransitionPage("On va commencer le process de performance de l'amplificateur 1.5T - Banc 4 - ", self.next_step, first=True))
        self.add_step("AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V", "Cabinet_alim.png", security=True)
        self.stack.addWidget(TransitionPage("Partie 1 du process :\nIdentification du matériel", self.next_step, image_path="IDN.png"))
        
        # Transition vers la partie Identification matériel
        self.add_step("Identification matériel - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Identification matériel - Étape 2 : Identifier  l'amplificateur avant de l'utiliser / l'installer","Amplifier.png")
        self.add_step("Identification matériel - Étape 3 : Identifier les instruments de mesures à piloter","Materials_VNA.png")

        # Transition vers la partie Câblage
        self.stack.addWidget(TransitionPage("Partie 2 du process :\nCâblage IHM", self.next_step, image_path="Cablage.png"))

        # Étapes Câblage IHM
        self.add_step("Câblage - Étape 1 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage - Étape 2 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage - Étape 3 : Fermé  VS Ouvert","Amplifier_O&C.png")
        self.add_step("Câblage - Étape 4 : Identifier le module","Combiner_Module.png")
        self.add_step("Câblage - Étape 5 : Brancher l'amplificateur au boitier de communication", "COM.png")
        self.add_step("Câblage - Étape 6 : Connecter les MXO34 & 33500B à l'ordinateur", "USB.png")
        self.add_step("Câblage - Étape 7 : Eeffectuer le câblage suivant", "VNA_Cablage_Body.png")

        # Transition vers la partie Alimentation
        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche", self.next_step, image_path="Mise_en_marche.png"))

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        # Transition vers IHM 3
        self.stack.addWidget(TransitionPage("Partie 4 du process :\n Commençons la partie mesure", self.next_step, image_path="Mesure.png"))
        self.stack.addWidget(MeasurePage(self.p5000a, self.swg33522B, self.swg33611A, self.mxo3, self.srfd_com))
        self.stack.setCurrentIndex(self.current)

    def add_step(self, titre, image, security=False):
        self.stack.addWidget(Step(titre, image, self.next_step, self.prev_step, security))

    def next_step(self):
        self.current += 1
        self.stack.setCurrentIndex(self.current)

    def prev_step(self):
        self.current -= 1
        self.stack.setCurrentIndex(self.current)
