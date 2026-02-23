#-------------------------------------------------------------------
# IMPORT DES LIBRAIRIES
#-------------------------------------------------------------------
import sys
import pyvisa
from srfd_lib import amp, vna
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QHBoxLayout, QCheckBox, QLineEdit, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIntValidator
from PyQt5.QtCore import Qt, QSize
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import csv
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet



#-------------------------------------------------------------------
# Couleurs
#-------------------------------------------------------------------
GE_PURPLE = "#4B0082"


#-------------------------------------------------------------------
# Log in page - utilisateur
#-------------------------------------------------------------------
class LoginPage(QWidget):
    def __init__(self, next_callback):
        super().__init__()
        layout = QVBoxLayout()

        self.sso_field = QLineEdit(); self.sso_field.setPlaceholderText("Operator ID (SSO)")
        self.nom_field = QLineEdit(); self.nom_field.setPlaceholderText("Nom")
        self.prenom_field = QLineEdit(); self.prenom_field.setPlaceholderText("Prénom")
        self.dept_field = QLineEdit(); self.dept_field.setPlaceholderText("Département")

        self.serial_field = QLineEdit(); self.serial_field.setPlaceholderText("DUT Serial Number")
        self.pn_field = QLineEdit(); self.pn_field.setPlaceholderText("Part Number")
        self.pn_rev_field = QLineEdit(); self.pn_rev_field.setPlaceholderText("PN Revision")
        self.test_date_field = QLineEdit(); self.test_date_field.setPlaceholderText("Test Date (YYYY-MM-DD)")
        self.station_field = QLineEdit(); self.station_field.setPlaceholderText("Station ID")

        for w in [
            self.sso_field, self.nom_field, self.prenom_field, self.dept_field,
            self.serial_field, self.pn_field, self.pn_rev_field,
            self.test_date_field, self.station_field
        ]:
            layout.addWidget(w)

        btn = QPushButton("Valider")
        btn.clicked.connect(lambda: self.save_and_next(next_callback))
        layout.addWidget(btn)

        self.setLayout(layout)

    def save_and_next(self, next_callback):
        self.parent().parent().user_info = {
            "SSO": self.sso_field.text(),
            "Nom": self.nom_field.text(),
            "Prenom": self.prenom_field.text(),
            "Departement": self.dept_field.text(),
            "DUT_Serial": self.serial_field.text(),
            "Part_Number": self.pn_field.text(),
            "PN_Revision": self.pn_rev_field.text(),
            "Test_Date": self.test_date_field.text(),
            "Station_ID": self.station_field.text()
        }
        next_callback()



#-------------------------------------------------------------------
# Classe step
#-------------------------------------------------------------------
class Step(QWidget):
    def __init__(self, titre, image_path, next_callback, back_callback=None, security=False, first_step=False):
        super().__init__()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Titre + logo à droite
        top_layout = QHBoxLayout()
        title = QLabel(titre)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo_pix = QPixmap("Pics/GE_Logo.png")
        if not logo_pix.isNull():
            logo.setPixmap(logo_pix.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignRight | Qt.AlignTop)

        top_layout.addWidget(title, stretch=1)
        top_layout.addWidget(logo, stretch=0)
        layout.addLayout(top_layout)

        # Image
        pixmap = QPixmap("Pics/" + image_path)
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaled(QSize(1900, 610), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            img_label.setText("Image manquante")
        layout.addWidget(img_label)


        # Boutons
        btn_layout = QHBoxLayout()
        self.done = False
        self.defaut = False

        # Bouton Retour (uniquement si pas la première étape)
        if back_callback and not first_step:
            back_btn = QPushButton("Retour")
            back_btn.setFont(QFont("Arial", 12, QFont.Bold))
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: gray; 
                    color: white; 
                    padding: 8px 20px; 
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #606060;
                }
            """)
            back_btn.clicked.connect(back_callback)
            btn_layout.addWidget(back_btn)

        # Bouton rouge "Défaut"
        defaut_btn = QPushButton("Défaut")
        defaut_btn.setFont(QFont("Arial", 12, QFont.Bold))
        defaut_btn.setStyleSheet("""
            QPushButton {
                background-color: red; 
                color: white; 
                padding: 8px 20px; 
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        defaut_btn.clicked.connect(self.mark_defaut)
        btn_layout.addWidget(defaut_btn)

        # Bouton vert "Fait"
        fait_btn = QPushButton("Fait")
        fait_btn.setFont(QFont("Arial", 12, QFont.Bold))
        fait_btn.setStyleSheet("""
            QPushButton {
                background-color: green; 
                color: white; 
                padding: 8px 20px; 
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
        """)
        fait_btn.clicked.connect(self.mark_done)
        btn_layout.addWidget(fait_btn)

        # Bouton Valider
        if security:
            self.checkbox = QCheckBox("J'ai pris connaissance de l'information")
            self.checkbox.setStyleSheet(f"color: {GE_PURPLE}; font-weight: bold;")
            layout.addWidget(self.checkbox)

            validate_btn = QPushButton("Valider")
            validate_btn.setFont(QFont("Arial", 12, QFont.Bold))
            validate_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GE_PURPLE}; 
                    color: white; 
                    padding: 8px 20px; 
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: #5C1AA3;
                }}
            """)
            validate_btn.setEnabled(False)

            def toggle_btn():
                validate_btn.setEnabled(self.checkbox.isChecked())

            self.checkbox.stateChanged.connect(toggle_btn)
            validate_btn.clicked.connect(lambda: self.try_next(next_callback))
            btn_layout.addWidget(validate_btn)
        else:
            btn = QPushButton("Valider")
            btn.setFont(QFont("Arial", 12, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GE_PURPLE}; 
                    color: white; 
                    padding: 8px 20px; 
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: #5C1AA3;
                }}
            """)
            btn.clicked.connect(lambda: self.try_next(next_callback))
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)


    def show_defaut_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Étape non validée")
        msg.setText("⚠️ Cette étape doit être obligatoirement réalisée.\nImpossible de passer à la suivante.")
        msg.exec_()

    def mark_defaut(self):
        self.defaut = True
        self.done = False
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Étape en défaut")
        msg.setText("⚠️ Cette étape est en défaut.\nImpossible de passer à la suivante tant que ce n'est pas corrigé.")
        msg.exec_()

    def mark_done(self):
        self.done = True
        self.defaut = False

    def try_next(self, next_callback):
        if self.done and not self.defaut:
            next_callback()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Validation requise")
            if self.defaut:
                msg.setText("⚠️ Étape en défaut.\nImpossible de valider tant que ce n'est pas corrigé.")
            else:
                msg.setText("⚠️ Vous devez cliquer sur 'Fait' avant de valider.")
            msg.exec_()


#-------------------------------------------------------------------
# Classe transition
#-------------------------------------------------------------------
class TransitionPage(QWidget):
    def __init__(self, message, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel(message)
        font_size = 32 if first else 26
        label.setFont(QFont("Arial", font_size, QFont.Bold))
        label.setStyleSheet(f"color: {GE_PURPLE};")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        if image_path:
            pixmap = QPixmap("Pics/" + image_path)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            if not pixmap.isNull():
                img_label.setPixmap(pixmap.scaled(QSize(1900, 600), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img_label.setText("Image manquante")
            layout.addWidget(img_label)

        btn = QPushButton("Suivant")
        btn.setFont(QFont("Arial", 12, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GE_PURPLE}; 
                color: white; 
                padding: 12px 30px; 
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #5C1AA3;
            }}
        """)
        btn.clicked.connect(next_callback)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

def export_results(output_list, user_info, timestamp):
    base = f"SRFD_InputGain_Report_{timestamp}"
    csv_filename = base + ".csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Champ", "Valeur"])
        for k, v in user_info.items():
            writer.writerow([k, v])

        writer.writerow([])
        writer.writerow(["Résultats", ""])

        for line in output_list:
            writer.writerow([line])

    return csv_filename

#-------------------------------------------------------------------
# Classe Mesure
#-------------------------------------------------------------------
class MeasurePage(QWidget):
    def __init__(self, p5000a, swg33522B, swg33611A, mxo3, srfd_com):
        super().__init__()
        self.p5000a = p5000a
        self.swg33522B = swg33522B
        self.swg33611A = swg33611A
        self.mxo3 = mxo3
        self.srfd_com = srfd_com
        layout = QVBoxLayout()
        title = QLabel("Mesure VNA – Gain Flatness / Amplification / Interpulse Stability")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color:{GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        layout.addWidget(self.out)
        btn = QPushButton("Lancer les mesures")
        btn.clicked.connect(self.run)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def run(self):
        self.out.clear()
        try:
            amp.poweroff(self.srfd_com)
            vswr, flatness = vna.gain_flatness(self.p5000a, self.srfd_com, self.swg33522B, self.swg33611A, self.mxo3)
            vna.amplification(self.p5000a, self.srfd_com, self.swg33522B, self.swg33611A, self.mxo3)
            gain_stab, phase_stab = vna.interpulse_stability(self.p5000a, self.srfd_com, self.swg33522B, self.swg33611A, self.mxo3)
            self.out.append(f"Gain flatness: {round(flatness,2)} dB")
            self.out.append(f"VSWR: {round(vswr,2)} :1")
            self.out.append(f"Interpulse gain stability: {round(gain_stab,2)} dB")
            self.out.append(f"Interpulse phase stability: {round(phase_stab,2)} °")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
        finally:

            amp.poweroff(self.srfd_com)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"SRFD_VNA_Report_{ts}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []


            story.append(Image("Pics/GE_Logo.png", width=80, height=80))
            story.append(Spacer(1, 16))

            # Infos utilisateur
            user = self.parent().parent().user_info
            story.append(Paragraph("<b>Rapport Utilisateur</b>", styles["Heading3"]))
            story.append(Paragraph(f"SSO: {user.get('SSO','')}", styles["Normal"]))
            story.append(Paragraph(f"Nom: {user.get('Nom','')}", styles["Normal"]))
            story.append(Paragraph(f"Prénom: {user.get('Prenom','')}", styles["Normal"]))
            story.append(Paragraph(f"Département: {user.get('Departement','')}", styles["Normal"]))
            story.append(Paragraph(f"DUT Serial Number: {user.get('DUT_Serial','')}", styles["Normal"]))
            story.append(Paragraph(f"Part Number: {user.get('Part_Number','')}", styles["Normal"]))
            story.append(Paragraph(f"PN Revision: {user.get('PN_Revision','')}", styles["Normal"]))
            story.append(Paragraph(f"Test Date: {user.get('Test_Date','')}", styles["Normal"]))
            story.append(Paragraph(f"Station ID: {user.get('Station_ID','')}", styles["Normal"]))
            story.append(Spacer(1, 16))

            user = self.parent().parent().user_info
            story.append(Paragraph("<b>Rapport Utilisateur</b>", styles["Heading3"]))
            for k, v in user.items():
                story.append(Paragraph(f"{k}: {v}", styles["Normal"]))
            story.append(Spacer(1, 16))
            
            story.append(Paragraph("<b>Résultats VNA</b>", styles["Heading3"]))
            for line in self.out.toPlainText().split("\n"):
                story.append(Paragraph(line, styles["Normal"]))

            doc.build(story)
            self.out.append(f"\nPDF généré : {filename}")
            
            # Construction liste CSV
            output_list = []

            # Résultats VNA (tout ce qui est affiché dans la zone texte)
            for line in self.out.toPlainText().split("\n"):
                output_list.append("VNA: " + line)

            # Export CSV
            csv_file = export_results(output_list, user, ts)
            self.out.append(f"Export CSV effectué : {csv_file}")



#-------------------------------------------------------------------
# Classe mainwidow + IHM
#-------------------------------------------------------------------
class MainWindow(QWidget):
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
        rm = pyvisa.ResourceManager()
        rm_rs232 = pyvisa.ResourceManager('@py')
        self.p5000a = rm.open_resource("TCPIP0::SH-749W4X3::hislip_PXI10_CHASSIS1_SLOT1_INDEX0::INSTR")
        self.p5000a.timeout = 5000
        self.swg33522B = rm.open_resource("USB0::0x0957::0x2C07::MY62000370::0::INSTR")
        self.swg33611A = rm.open_resource("USB0::0x0957::0x4807::MY59003502::0::INSTR")
        self.mxo3 = rm.open_resource("USB0::0x0AAD::0x0197::1335.2050k04-101365::0::INSTR")
        self.srfd_com = rm_rs232.open_resource("ASRL5::INSTR")
        self.srfd_com.baud_rate = 9600
        self.srfd_com.data_bits = 8
        self.srfd_com.stop_bits = pyvisa.constants.StopBits.one
        self.srfd_com.parity = pyvisa.constants.Parity.none
        self.srfd_com.timeout = 2000
        self.current = 0
# -------------------
        # Pages d’intro
        # -------------------
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


#-------------------------------------------------------------------
# Main
#-------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

#-------------------------------------------------------------------
# Fin du programme
#-------------------------------------------------------------------