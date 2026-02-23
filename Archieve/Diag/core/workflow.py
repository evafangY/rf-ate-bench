from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from Diag.ui.login_page import LoginPage
from Diag.ui.step_page import Step
from Diag.ui.transition_page import TransitionPage
from Diag.core.measure_page import MeasurePage
from Diag.core.visa_setup import connect_instruments

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow GE Healthcare")
        self.resize(900, 700)

        # Stack
        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Instruments
        srfd_com, srfd_amp_master, srfd_amp_slave, com_status = connect_instruments()

        if com_status is True:
            print("Communication OK du premier coup")
        #elif com_status is False:
           # print("⚠️ Première tentative échouée → Reconnexion réussie")
        else:
            print("❌ Communication impossible avec les instruments")

        self.srfd_com = srfd_com
        self.srfd_amp_master = srfd_amp_master
        self.srfd_amp_slave = srfd_amp_slave

        # User info
        self.user_info = {}

        # First page
        self.login_page = LoginPage(self.next_step)
        self.stack.addWidget(self.login_page)


        # Intro
        self.stack.addWidget(
            TransitionPage(
                "On va commencer le process de diagnostique de l'amplificateur 1.5T - Banc 0 - ",
                self.next_step,
                first=True
            )
        )

        # Steps
        self.add_step("AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V",
                      "Cabinet_alim.png", security=True)

        self.stack.addWidget(TransitionPage("Partie 1 du process :\nCâblage COM",
                                            self.next_step, image_path="COM.png"))

        self.add_step("Câblage COM - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Câblage COM - Étape 2 : Identifier l'amplificateur avant de l'utiliser / l'installer",
                      "Amplifier.png", first_step=True)
        self.add_step("Câblage COM - Étape 3 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage COM - Étape 4 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage COM - Étape 5 : Résultat", "Amplificateur_ouvert.png")
        self.add_step("Câblage COM - Étape 6 : Brancher le câble de COM sur l'amplificateur du haut",
                      "Master_connection.png")
        self.add_step("Câblage COM - Étape 7 : Brancher le câble de COM sur l'amplificateur du bas",
                      "Slave_connection.png")

        # Transition
        self.stack.addWidget(TransitionPage("Partie 2 du process :\nAlimentation",
                                            self.next_step, image_path="Alimentation.png"))

        # Alimentation steps
        self.add_step("Alimentation - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Alimentation - Étape 2 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Alimentation - Étape 3 : Vérifier et mettre les équipements de protection individuels", "EPI.png")
        self.add_step("Alimentation - Étape 4 : Tester l'appareil avant de l'utiliser", "VAT_Test.png")
        self.add_step("Alimentation - Étape 5 : Vérification de l'absence de tension", "VAT_Verification.png")
        self.add_step("Alimentation - Étape 6 : Lier l'amplificateur et le PDU à travers le câble d'alimentation",
                      "Triphase.png", security=True)
        self.add_step("Alimentation - Étape 7 : Mettre la vitre isolante pour plus de protection",
                      "Vitre_isolante.png")

        # Transition
        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche",
                                            self.next_step, image_path="Mise_en_marche.png"))

        # Mise en marche
        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur",
                      "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité",
                      "Security.png", security=True)

        # Final measure page
        self.stack.addWidget(MeasurePage(self.srfd_com, self.srfd_amp_master, self.srfd_amp_slave))

        # Init index
        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)

    def add_step(self, titre, image, security=False, first_step=False):
        step = Step(titre, image, self.next_step, self.prev_step,
                    security=security, first_step=first_step)
        self.stack.addWidget(step)

    def next_step(self):
        self.current_index += 1
        if self.current_index < self.stack.count():
            self.stack.setCurrentIndex(self.current_index)

    def prev_step(self):
        self.current_index -= 1
        if self.current_index >= 0:
            self.stack.setCurrentIndex(self.current_index)
