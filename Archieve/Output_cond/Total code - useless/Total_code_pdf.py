#-------------------------------------------------------------------
# IMPORT DES LIBRAIRIES
#-------------------------------------------------------------------
import sys, time, math, datetime
import pandas as pd
import pyvisa
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QHBoxLayout, QCheckBox, QLineEdit, QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIntValidator
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import csv
import pandas as pd
from reportlab.lib.utils import ImageReader



#-------------------------------------------------------------------
# Connexion + config instruments
#-------------------------------------------------------------------
SCOPE_ADDR = "USB0::0x0AAD::0x0197::1335.2050k04-101598::0::INSTR"
SWG_ADDR   = "USB0::0x0957::0x4807::MY59003502::0::INSTR"

def connect_instruments():
    rm = pyvisa.ResourceManager()
    scope = rm.open_resource(SCOPE_ADDR); scope.timeout = 10000
    swg33611A = rm.open_resource(SWG_ADDR); swg33611A.timeout = 5000
    return rm, scope, swg33611A

def scope_output_cond_setup(scope, mode="Body"):
    scope.write("*RST")
    scope.write("CHANnel1:COUPling DC")
    scope.write("CHANnel2:COUPling DC")
    scope.write("CHANnel3:COUPling DC")
    scope.write("CHANnel4:COUPling DC")
    scope.write("TRIGger:MODE NORMal")
    scope.write("CHANnel1:BANDwidth 350E6")
    scope.write("CHANnel2:BANDwidth 350E6")
    scope.write("CHANnel3:BANDwidth 350E6")
    scope.write("CHANnel4:BANDwidth 350E6")
    scope.write("TRIGger:EVENt1:SOURce EXTernanalog")
    scope.write("TRIGger:ANEDge:LEVel 0.8")
    scope.write("TRIGger:ANEDge:COUPling DC")
    scope.write("TIMebase:SCALe 1E-8")
    scope.write("CHANnel1:SCALe 1")
    #scope.write("CHANnel2:SCALe 0.004")
    scope.write("CHANnel3:SCALe 0.001")
    #scope.write("CHANnel4:SCALe 0.004")
    scope.write("CHANnel1:STATe ON")
    scope.write("CHANnel2:STATe ON")
    scope.write("CHANnel3:STATe ON")
    scope.write("CHANnel4:STATe ON")
    scope.write("MEASurement1:MAIN CYCRms")
    scope.write("MEASurement1:SOURce C1")
    scope.write("MEASurement2:MAIN CYCRms")
    scope.write("MEASurement2:SOURce C2")
    scope.write("MEASurement3:MAIN CYCRms")
    scope.write("MEASurement3:SOURce C3")
    scope.write("MEASurement4:MAIN CYCRms")
    scope.write("MEASurement4:SOURce C4")
    scope.write("ACQuire:TYPE AVERage")
    scope.write("ACQuire:COUNt 100")
    scope.query("*OPC?")

    if mode == "Body":
        scope.write("CHANnel2:SCALe 0.004")
        scope.write("CHANnel4:SCALe 0.004")
    else:
        scope.write("CHANnel2:SCALe 0.010")
        scope.write("CHANnel4:SCALe 0.010")

def swg_output_cond_setup(swg33611A):
    swg33611A.write("*RST")
    swg33611A.write("OUTPut1:LOAD 50")
    swg33611A.write("SOURce1:FUNCtion SIN")
    swg33611A.write("SOURCE1:FREQUENCY 63860000")
    swg33611A.write("SOURCE1:VOLT:UNIT DBM")
    swg33611A.write("SOURCE1:VOLT 22")
    swg33611A.write("OUTPUT1 ON")
    swg33611A.query("*OPC?")

def configure(scope, swg33611A, mode="Body"):
    swg_output_cond_setup(swg33611A)
    scope_output_cond_setup(scope, mode)
    time.sleep(1)

#-------------------------------------------------------------------
# Mesure Body 
#-------------------------------------------------------------------
def measure_body(scope):
    scope.write("MEASurement1:RESult:ACTual?"); mJ4 = float(scope.read())
    scope.write("MEASurement2:RESult:ACTual?"); mJ6 = float(scope.read())
    scope.write("MEASurement3:RESult:ACTual?"); mJ10 = float(scope.read())
    scope.write("MEASurement4:RESult:ACTual?"); mJ8 = float(scope.read())
    gJ6 = round(-20*math.log10(mJ6/mJ4),2)
    gJ8 = round(-20*math.log10(mJ8/mJ4),2)
    gJ10 = round(-20*math.log10(mJ10/mJ4),2)
    return {
        "J4": mJ4,
        "J6": gJ6,
        "J8": gJ8,
        "J10": gJ10
    }


#-------------------------------------------------------------------
# Mesure Head 
#-------------------------------------------------------------------
def measure_head(scope):
    scope.write("MEASurement1:RESult:ACTual?"); J3 = float(scope.read())
    scope.write("MEASurement2:RESult:ACTual?"); J5 = float(scope.read())
    scope.write("MEASurement3:RESult:ACTual?"); J9 = float(scope.read())
    scope.write("MEASurement4:RESult:ACTual?"); J7 = float(scope.read())
    return {
        "J3":J3,
        "J5":round(-20*math.log10(J5/J3),2),
        "J7":round(-20*math.log10(J7/J3),2),
        "J9":round(-20*math.log10(J9/J3),2)}


#-------------------------------------------------------------------
# Couleurs
#-------------------------------------------------------------------
GE_PURPLE = "#4B0082"
#GE_LIGHT_PURPLE = "#F5F0FA"


#-------------------------------------------------------------------
# Log in page - utilisateur
#-------------------------------------------------------------------
# -------------------------
# Login Page
# -------------------------
class LoginPage(QWidget):
    def __init__(self, next_callback):
        super().__init__()
        layout = QVBoxLayout()

        # Champs existants
        self.sso_field = QLineEdit(); self.sso_field.setPlaceholderText("Operator ID (SSO)")
        self.nom_field = QLineEdit(); self.nom_field.setPlaceholderText("Nom")
        self.prenom_field = QLineEdit(); self.prenom_field.setPlaceholderText("Prénom")
        self.dept_field = QLineEdit(); self.dept_field.setPlaceholderText("Département")

        # Nouveaux champs demandés
        self.serial_field = QLineEdit(); self.serial_field.setPlaceholderText("DUT Serial Number")
        self.pn_field = QLineEdit(); self.pn_field.setPlaceholderText("Part Number")
        self.pn_rev_field = QLineEdit(); self.pn_rev_field.setPlaceholderText("PN Revision")
        self.test_date_field = QLineEdit(); self.test_date_field.setPlaceholderText("Test Date (YYYY-MM-DD)")
        self.station_field = QLineEdit(); self.station_field.setPlaceholderText("Station ID")

        # Ajout dans l’UI
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
# Classe transition
#-------------------------------------------------------------------
class TransitionPage(QWidget):
    def __init__(self, message, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()

        # Texte
        label = QLabel(message)
        font_size = 32 if first else 26
        label.setFont(QFont("Arial", font_size, QFont.Bold))
        label.setStyleSheet(f"color: {GE_PURPLE};")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Image optionnelle
        if image_path:
            pixmap = QPixmap("Pics/" + image_path)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            if not pixmap.isNull():
                img_label.setPixmap(pixmap.scaled(QSize(1900, 600), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img_label.setText("Image manquante")
            layout.addWidget(img_label)

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


def export_results(output_list, user_info, timestamp):
    base = f"SRFD_Report_{timestamp}"

    # CSV
    csv_filename = base + ".csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Champ", "Valeur"])
        for key, val in user_info.items():
            writer.writerow([key, val])
        writer.writerow([])
        writer.writerow(["Résultats", ""])
        for line in output_list:
            writer.writerow([line, ""])

    return csv_filename

#-------------------------------------------------------------------
# Classe mesure BODY
#-------------------------------------------------------------------
class MeasureBodyPage(QWidget):
    def __init__(self, scope, swg33611A, next_callback, back_callback=None):
        super().__init__()
        self.scope = scope
        self.swg33611A = swg33611A
        self.next_callback = next_callback
        self.back_callback = back_callback
        self.done = False
        self.defaut = False

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Résultats
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # Label de statut
        self.loading_label = QLabel("Mesure en cours…")
        self.loading_label.setStyleSheet("background-color:#4B0082; color:white; font-weight:bold; padding:6px; border-radius:8px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        # Bouton lancer mesure
        btn_measure = QPushButton("Lancer mesure BODY")
        btn_measure.setFont(QFont("Arial", 12, QFont.Bold))
        btn_measure.setStyleSheet("background-color:green; color:white; padding:8px; border-radius:8px;")
        btn_measure.clicked.connect(self.run_measure)
        layout.addWidget(btn_measure)

        # Bouton suivant
        btn_next = QPushButton("Suivant")
        btn_next.setFont(QFont("Arial", 12, QFont.Bold))
        btn_next.setStyleSheet(f"background-color:{GE_PURPLE}; color:white; padding:10px; border-radius:8px;")
        btn_next.clicked.connect(next_callback)
        layout.addWidget(btn_next)

        self.setLayout(layout)

    def run_measure(self):
        try:
            self.loading_label.show()
            QApplication.processEvents()
            configure(self.scope, self.swg33611A, "Body")
            results = measure_body(self.scope)
            text = "Mesures BODY:\n" + "\n".join([f"{k}: {v}" for k,v in results.items()])
            self.result_display.setText(text)
            self.parent().parent().body_results = results
            self.done = True
        except Exception as e:
            self.result_display.setText(f"❌ Erreur mesure BODY:\n{str(e)}")
            self.defaut = True
        finally:
            self.loading_label.hide()


#-------------------------------------------------------------------
# Classe mesure HEAD
#-------------------------------------------------------------------
class MeasureHeadPage(QWidget):
    def __init__(self, scope, swg33611A, next_callback, back_callback=None):
        super().__init__()
        self.scope = scope
        self.swg33611A = swg33611A
        self.next_callback = next_callback
        self.back_callback = back_callback
        self.done = False
        self.defaut = False

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Résultats
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # Label de statut
        self.loading_label = QLabel("Mesure en cours…")
        self.loading_label.setStyleSheet("""
            QLabel {
                background-color: #4B0082;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 8px;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        # Bouton lancer mesure
        btn_measure = QPushButton("Lancer mesure HEAD")
        btn_measure.setFont(QFont("Arial", 12, QFont.Bold))
        btn_measure.setStyleSheet("background-color:green; color:white; padding:8px; border-radius:8px;")
        btn_measure.clicked.connect(self.run_measure)
        layout.addWidget(btn_measure)

        # Bouton suivant
        btn_next = QPushButton("Suivant")
        btn_next.setFont(QFont("Arial", 12, QFont.Bold))
        btn_next.setStyleSheet(f"background-color:{GE_PURPLE}; color:white; padding:10px; border-radius:8px;")
        btn_next.clicked.connect(next_callback)
        layout.addWidget(btn_next)

        self.setLayout(layout)

    def run_measure(self):
        try:
            self.loading_label.show()
            QApplication.processEvents()
            configure(self.scope, self.swg33611A, "Head")
            results = measure_head(self.scope)
            text = "Mesures HEAD:\n" + "\n".join([f"{k}: {v}" for k,v in results.items()])
            self.result_display.setText(text)

            # Sauvegarde Body + Head
            body = getattr(self.parent().parent(), "body_results", None)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            data = []
            if body:
                data.append({"Type":"BODY", **body})
            data.append({"Type":"HEAD", **results})
            filename = f"SRFD_Measures_{ts}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            story.append(Image("Pics/GE_Logo.png", width=80, height=80))
            story.append(Spacer(1, 20))
            user = self.parent().parent().user_info
            story.append(Paragraph("<b>Rapport Utilisateur</b>", styles["Heading2"]))
            story.append(Paragraph(f"SSO: {user['SSO']}", styles["Normal"]))
            story.append(Paragraph(f"Nom: {user['Nom']}", styles["Normal"]))
            story.append(Paragraph(f"Prénom: {user['Prenom']}", styles["Normal"]))
            story.append(Paragraph(f"Département: {user['Departement']}", styles["Normal"]))
            story.append(Paragraph(f"DUT Serial Number: {user['DUT_Serial']}", styles["Normal"]))
            story.append(Paragraph(f"Part Number: {user['Part_Number']}", styles["Normal"]))
            story.append(Paragraph(f"PN Revision: {user['PN_Revision']}", styles["Normal"]))
            story.append(Paragraph(f"Test Date: {user['Test_Date']}", styles["Normal"]))
            story.append(Paragraph(f"Station ID: {user['Station_ID']}", styles["Normal"]))

            story.append(Spacer(1, 20))

            story.append(Paragraph("<b>Résultats Mesures</b>", styles["Heading2"]))

            for entry in data:
                story.append(Paragraph(f"<b>{entry['Type']}</b>", styles["Normal"]))

                for k,v in entry.items():
                    if k!="Type": story.append(Paragraph(f"{k}: {v}", styles["Normal"]))
                story.append(Spacer(1, 12))
            doc.build(story)

            # Export PDF
            self.result_display.append(f"\n✅ Export PDF effectué : {filename}")

            # Construction de la liste pour le CSV
            output_list = []
            if body:
                output_list += [f"BODY {k}: {v}" for k, v in body.items()]
            output_list += [f"HEAD {k}: {v}" for k, v in results.items()]

            # Export CSV
            csv_file = export_results(output_list, user, ts)
            self.result_display.append(f"\n ✅Export CSV effectué : SRFD_Measures_{csv_file}")
            self.done = True

        except Exception as e:
            self.result_display.setText(f"❌ Erreur mesure HEAD:\n{str(e)}")
            self.defaut = True
        finally:
            self.loading_label.hide()


#-------------------------------------------------------------------
# Classe mainwindow + IHM
#-------------------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow SRFD II")
        self.resize(900,700)
        self.stack = QStackedWidget()
        layout = QVBoxLayout(); layout.addWidget(self.stack); self.setLayout(layout)
        self.rm,self.scope,self.swg33611A = connect_instruments()

        self.user_info = {}
        self.stack.addWidget(LoginPage(self.next_step))

        self.stack.addWidget(TransitionPage("On va commencer le process du Tune Output", self.next_step, first=True))

        # Transition vers la partie Identification matériel
        self.stack.addWidget(TransitionPage("Partie 1 du process :\nIdentification du matériel", self.next_step, image_path="IDN.png"))
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
        self.add_step("Câblage - Étape 5 : Connexion entre les instruments & le module combiner", "Combiner_connection.png")
        self.add_step("Câblage - Étape 6 : Connecter le module à l'oscilloscope - Mode Body", "Oscilloscope_Body.png")

        # Transition vers la partie Alimentation
        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche", self.next_step, image_path="Mise_en_marche.png"))

        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        self.stack.addWidget(TransitionPage("Partie 4 : Mesure BODY", self.next_step, image_path="MesureBody.png"))
        self.add_step("Mesure - Étape  : Connecter le module à l'oscilloscope - Mode Head", "Oscilloscope_Body.png")
        self.stack.addWidget(MeasureBodyPage(self.scope, self.swg33611A, self.next_step))

        self.stack.addWidget(TransitionPage("Partie 5 : Câblage pour HEAD", self.next_step, image_path="MesureHead.png"))
        self.add_step("Câblage - Étape 8 : Connecter le module à l'oscilloscope - Mode Head", "Oscilloscope_Head.png")
        self.stack.addWidget(MeasureHeadPage(self.scope, self.swg33611A, self.next_step))


        self.current_index=0; self.stack.setCurrentIndex(self.current_index)

    def add_step(self, titre, image, security=False, first_step=False):
        step=Step(titre,image,self.next_step,self.prev_step)
        self.stack.addWidget(step)

    def next_step(self):
        self.current_index += 1
        if self.current_index < self.stack.count():
            self.stack.setCurrentIndex(self.current_index)

    def prev_step(self):
        self.current_index -= 1
        if self.current_index >= 0:
            self.stack.setCurrentIndex(self.current_index)


# ------------------------------------------------------------------
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