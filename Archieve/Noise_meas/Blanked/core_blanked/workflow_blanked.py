from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from Noise_meas.Blanked.ui_blanked.login_page_blanked import LoginPage
from Noise_meas.Blanked.ui_blanked.step_page_blanked import Step
from Noise_meas.Blanked.ui_blanked.transition_page_blanked import TransitionPage
from Noise_meas.Blanked.core_blanked.measure_page_lna_blanked import MeasurePage_LNA

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow GE Healthcare")
        self.resize(900, 700)

        self.user_info = {}

        self.stack = QStackedWidget()
        self.stack.addWidget(LoginPage(self.next_step))

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.stack.addWidget(TransitionPage(
            "On va commencer le process de Noise Blanked de l'amplificateur 1.5T - Banc 5 - ",
            self.next_step,
            first=True
        ))

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
        self.add_step("Câblage COM - Étape 6 : Effectuer le câblage suivant pour le LNA", "Cablage_blanking.png")
        self.add_step("Câblage COM - Étape 7 : Effectuer le câblage suivant pour la communication", "Cablage_COM_Blanking.png")

        self.stack.addWidget(TransitionPage("Partie 2 du process :\nAlimentation",
                                            self.next_step, image_path="Alimentation.png"))

        self.add_step("Alimentation - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Alimentation - Étape 2 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Alimentation - Étape 3 : Vérifier et mettre les équipements de protection individuels", "EPI.png")
        self.add_step("Alimentation - Étape 4 : Tester l'appareil avant de l'utiliser", "VAT_Test.png")
        self.add_step("Alimentation - Étape 5 : Vérification de l'absence de tension", "VAT_Verification.png")
        self.add_step("Alimentation - Étape 6 : Lier l'amplificateur et le PDU à travers le câble d'alimentation",
                      "Triphase.png", security=True)
        self.add_step("Alimentation - Étape 7 : Mettre la vitre isolante pour plus de protection",
                      "Vitre_isolante.png")

        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche",
                                            self.next_step, image_path="Mise_en_marche.png"))

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur",
                      "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité",
                      "Security.png", security=True)

        self.stack.addWidget(MeasurePage_LNA())

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
