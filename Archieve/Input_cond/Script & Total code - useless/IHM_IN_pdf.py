#-------------------------------------------------------------------
# IMPORT DES LIBRAIRIES
#-------------------------------------------------------------------
import sys, time, math
import pyvisa, Libraries.input_gain_lib as input_gain_lib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QTextEdit, QMessageBox, QCheckBox, QLineEdit, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIntValidator
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import csv
import pandas as pd
from reportlab.lib.utils import ImageReader



#-------------------------------------------------------------------
# Couleurs
#-------------------------------------------------------------------
GE_PURPLE = "#4B0082"


#-------------------------------------------------------------------
# Connexion aux instruments
#-------------------------------------------------------------------
def connect_instruments():
    rm = pyvisa.ResourceManager()
    rm_rs232 = pyvisa.ResourceManager('@py')
    scope = rm.open_resource("USB0::0x0AAD::0x0197::1335.2050k04-101598::0::INSTR"); scope.timeout=5000
    swg33522B = rm.open_resource("USB0::0x0957::0x2C07::MY62000370::0::INSTR"); swg33522B.timeout=5000
    swg33611A = rm.open_resource("USB0::0x0957::0x4807::MY59003502::0::INSTR"); swg33611A.timeout=5000
    srfd_com = rm_rs232.open_resource("ASRL6::INSTR")
    srfd_com.baud_rate=9600; srfd_com.data_bits=8
    srfd_com.stop_bits=pyvisa.constants.StopBits.one
    srfd_com.parity=pyvisa.constants.Parity.none
    srfd_com.timeout=5000
    return scope, swg33522B, swg33611A, srfd_com


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
    def __init__(self, titre, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(titre)
        label.setFont(QFont("Arial", 26, QFont.Bold))
        label.setStyleSheet(f"color:{GE_PURPLE};")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        if image_path:
            pixmap = QPixmap("Pics/"+image_path)
            img = QLabel(); img.setAlignment(Qt.AlignCenter)
            if not pixmap.isNull():
                img.setPixmap(pixmap.scaled(QSize(1900,610), Qt.KeepAspectRatio))
            layout.addWidget(img)

        # Bouton Suivant
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
# classe mesure body 
#-------------------------------------------------------------------
class MeasureBodyPage(QWidget):
    def __init__(self, scope, swg33522B, swg33611A, srfd_com, next_callback):
        super().__init__()
        self.scope, self.swg33522B, self.swg33611A, self.srfd_com = scope, swg33522B, swg33611A, srfd_com
        self.next_callback = next_callback
        layout = QVBoxLayout()
        title = QLabel("Mesure BODY"); title.setFont(QFont("Arial",18,QFont.Bold))
        title.setStyleSheet(f"color:{GE_PURPLE};"); layout.addWidget(title)
        self.result_display = QTextEdit(); self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)
        valider = QPushButton("Lancer mesure BODY")
        valider.setStyleSheet(f"background-color:{GE_PURPLE}; color:white; padding:8px;")
        valider.clicked.connect(self.run_measure)
        layout.addWidget(valider)
        self.setLayout(layout)

    def run_measure(self):
        try:
            input_gain_lib.poweroff(self.srfd_com)
            input_gain_lib.config_scope(self.scope)
            input_gain_lib.config_blanking_swg(self.swg33522B)
            input_gain_lib.standby(self.srfd_com)
            input_gain_lib.body_mode(self.srfd_com)
            input_gain_lib.operate(self.srfd_com)

            # Vérif gain BODY
            input_gain_lib.config_rf_swg(self.swg33611A,"-20")
            while True:
                self.scope.write("MEASurement1:RESult:ACTual?")
                val = float(self.scope.read())
                power = 10*math.log10(val**2/50)+90
                self.result_display.setText(f"Puissance BODY: {round(power,2)} dBm")
                QApplication.processEvents()
                if 49.5 <= power <= 50.5:
                    break
                time.sleep(1)

            # Mesure finale gain
            input_gain_lib.config_rf_swg(self.swg33611A,"0")
            while True:
                self.scope.write("MEASurement1:RESult:ACTual?")
                val = float(self.scope.read())
                power = 10*math.log10(val**2/50)+90
                self.result_display.append(f"Puissance BODY (gain): {round(power,2)} dBm")
                QApplication.processEvents()
                if 71.9 <= power <= 72.1:
                    break
                time.sleep(1)

            self.next_callback()

            # Stocker les résultats BODY pour le PDF final
            self.parent().parent().body_results = self.result_display.toPlainText()

        except Exception as e:
            QMessageBox.critical(self,"Erreur",str(e))

        input_gain_lib.off(self.swg33522B, self.swg33611A)
        input_gain_lib.poweroff(self.srfd_com)


#-------------------------------------------------------------------
# classe mesure Head
#-------------------------------------------------------------------
class MeasureHeadPage(QWidget):
    def __init__(self, scope, swg33522B, swg33611A, srfd_com, next_callback=None):
        super().__init__()
        self.scope = scope
        self.swg33522B = swg33522B
        self.swg33611A = swg33611A
        self.srfd_com = srfd_com
        self.next_callback = next_callback

        layout = QVBoxLayout()

        # Titre
        title = QLabel("Mesure HEAD")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color:{GE_PURPLE};")
        layout.addWidget(title)

        # Zone résultats
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # Bouton lancer mesure
        valider = QPushButton("Lancer mesure HEAD")
        valider.setStyleSheet(f"background-color:{GE_PURPLE}; color:white; padding:8px;")
        valider.clicked.connect(self.run_measure)
        layout.addWidget(valider)

        self.setLayout(layout)

    def run_measure(self):
        try:
            # Initialisation instruments
            input_gain_lib.poweroff(self.srfd_com)
            input_gain_lib.config_scope(self.scope)
            input_gain_lib.config_blanking_swg(self.swg33522B)
            input_gain_lib.standby(self.srfd_com)
            input_gain_lib.head_mode(self.srfd_com)
            input_gain_lib.operate(self.srfd_com)

            # Mesure HEAD
            input_gain_lib.config_rf_swg(self.swg33611A, "0")
            while True:
                self.scope.write("MEASurement1:RESult:ACTual?")
                val = float(self.scope.read())
                power = 10 * math.log10(val**2 / 50) + 90
                self.result_display.setText(f"Puissance HEAD: {round(power,2)} dBm")
                QApplication.processEvents()
                if 62.9 <= power <= 63.1:
                    break
                time.sleep(1)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            # Shutdown propre
            input_gain_lib.off(self.swg33522B, self.swg33611A)
            input_gain_lib.poweroff(self.srfd_com)

            # ✅ Export PDF unique BODY + HEAD
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"SRFD_InputGain_Report_{ts}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Logo
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


            # Résultats BODY (stockés depuis MeasureBodyPage)
            body = getattr(self.parent().parent(), "body_results", None)
            if body:
                story.append(Paragraph("<b>Résultats BODY</b>", styles["Heading3"]))
                for line in body.split("\n"):
                    story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 12))

            # Résultats HEAD
            story.append(Paragraph("<b>Résultats HEAD</b>", styles["Heading3"]))
            for line in self.result_display.toPlainText().split("\n"):
                story.append(Paragraph(line, styles["Normal"]))

            doc.build(story)
            self.result_display.append(f"\n✅ Export PDF effectué : {filename}")

            # Construction liste CSV
            output_list = []

            body = getattr(self.parent().parent(), "body_results", None)
            if body:
                for line in body.split("\n"):
                    output_list.append("BODY: " + line)

            for line in self.result_display.toPlainText().split("\n"):
                output_list.append("HEAD: " + line)

            # Export CSV
            csv_file = export_results(output_list, user, ts)
            self.result_display.append(f" ✅Export CSV effectué : {csv_file}")


            # Callback si défini
            if self.next_callback:
                self.next_callback()


#-------------------------------------------------------------------
# classe mainwindow + IHM
#-------------------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow Input Gain")
        self.resize(900,700)
        self.stack = QStackedWidget(); layout=QVBoxLayout(); layout.addWidget(self.stack); self.setLayout(layout)
        scope,swg33522B,swg33611A,srfd_com = connect_instruments()

        self.user_info = {}
        self.stack.addWidget(LoginPage(self.next_step))

        self.stack.addWidget(TransitionPage("On va commencer le process du Input Tunning de l'amplificateur 1.5T - Banc 3 - ", self.next_step, first=True))
        self.add_step("AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V", "Cabinet_alim.png", security=True)
        self.stack.addWidget(TransitionPage("Partie 1 du process :\nIdentification du matériel", self.next_step, image_path="IDN.png"))
        
        # Transition vers la partie Identification matériel
        self.add_step("Identification matériel - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Identification matériel - Étape 2 : Identifier  l'amplificateur avant de l'utiliser / l'installer","Amplifier.png")
        self.add_step("Identification matériel - Étape 3 : Identifier les instruments de mesures à piloter","Materials.png")

        # Transition vers la partie Câblage
        self.stack.addWidget(TransitionPage("Partie 2 du process :\nCâblage", self.next_step, image_path="Cablage.png"))

        # Étapes Câblage IHM
        self.add_step("Câblage - Étape 1 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage - Étape 2 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage - Étape 3 : Fermé  VS Ouvert","Amplifier_O&C.png")
        self.add_step("Câblage - Étape 4 : Identifier le module","Combiner_Module.png")
        self.add_step("Câblage - Étape 5 : Brancher l'amplificateur au boitier de communication", "COM.png")
        self.add_step("Câblage - Étape 6 : Connecter les instruments à l'ordinateur", "USB.png")

        # Transition vers la partie Alimentation
        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche", self.next_step, image_path="Mise_en_marche.png"))

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        # Transition vers la partie Mesure Gain Body
        self.stack.addWidget(TransitionPage("Partie 4 : Mesure Body",self.next_step,"MesureBody.png"))
        self.add_step("Body Mode : Effectuer le câblage suivant pour le mode Body", "Body_cablage.png")
        self.stack.addWidget(MeasureBodyPage(scope,swg33522B,swg33611A,srfd_com,self.next_step))

        # Transition vers la partie Mesure Gain Head

        self.stack.addWidget(TransitionPage("Partie 5 : Mesure Head",self.next_step,"MesureHead.png"))
        self.add_step("Head Mode : Effectuer le câblage suivant pour le mode Head", "Head_cablage.png")
        self.stack.addWidget(MeasureHeadPage(scope,swg33522B,swg33611A,srfd_com))

        self.current_index=0; self.stack.setCurrentIndex(self.current_index)


    def add_step(self, titre, image, security=False, first_step=False):
        step = Step(titre, image, self.next_step, self.prev_step, security=security, first_step=first_step)
        self.stack.addWidget(step)

    def next_step(self):
        self.current_index += 1
        if self.current_index < self.stack.count():
            self.stack.setCurrentIndex(self.current_index)

    def prev_step(self):
        self.current_index -= 1
        if self.current_index >= 0:
            self.stack.setCurrentIndex(self.current_index)

    def finish(self):
        print("Workflow terminé !")
        self.close()


# ------------------------------------------------------------------
# Main
#-------------------------------------------------------------------
def main():
    app=QApplication(sys.argv)
    w=MainWindow(); w.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()

#-------------------------------------------------------------------
# Fin du programme
#-------------------------------------------------------------------