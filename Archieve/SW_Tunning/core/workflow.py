from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from SW_Tunning.ui.login_page import LoginPage
from SW_Tunning.ui.step_page import Step
from SW_Tunning.ui.transition_page import TransitionPage
from SW_Tunning.core.regulation_page import RegulationPage

class MainWindow(QWidget):
    def __init__(self, scope, srfd_com, srfd_amp_master, srfd_amp_slave):
        super().__init__()
        self.setWindowTitle("Workflow Régulation Amplificateur GE Healthcare")
        self.resize(900, 700)

        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.scope = scope
        self.srfd_com = srfd_com
        self.srfd_amp_master = srfd_amp_master
        self.srfd_amp_slave = srfd_amp_slave

        self.user_info = {}

        self.stack.addWidget(LoginPage(self.next_step))

        self.stack.addWidget(TransitionPage(
            "On va commencer le process du Tunning by Software de l'amplificateur 1.5T - Banc 2 - ",
            self.next_step,
            first=True
        ))

        self.add_step("AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V",
                      "Cabinet_alim.png", security=True)

        self.stack.addWidget(TransitionPage("Partie 1 du process :\nIdentification du matériel",
                                            self.next_step, image_path="IDN.png"))

        self.add_step("Identification matériel - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Identification matériel - Étape 2 : Identifier l'amplificateur avant de l'utiliser / l'installer", "Amplifier.png")
        self.add_step("Identification matériel - Étape 3 : Identifier les instruments de mesures à piloter", "Materials.png")

        self.stack.addWidget(TransitionPage("Partie 2 du process :\nCâblage IHM",
                                            self.next_step, image_path="Cablage.png"))

        self.add_step("Câblage - Étape 1 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage - Étape 2 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage - Étape 3 : Fermé VS Ouvert", "Amplifier_O&C.png")
        self.add_step("Câblage - Étape 4 : Identifier le module", "Combiner_Module.png")
        self.add_step("Câblage - Étape 5 : Connecter le boitier de communication à l'amplificateur Slave", "Slave_connection.png")
        self.add_step("Câblage - Étape 6 : Connecter le boitier de communication à l'amplificateur Master", "Master_connection.png")
        self.add_step("Câblage - Étape 7 : Connecter l'amplificateur au boitier de communication", "COM.png")
        self.add_step("Câblage - Étape 8 : Connecter les instruments à l'ordinateur", "USB.png")

        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche",
                                            self.next_step, image_path="Mise_en_marche.png"))

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        self.stack.addWidget(RegulationPage(self.scope, self.srfd_com, self.srfd_amp_master, self.srfd_amp_slave, self.next_step))

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)

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
