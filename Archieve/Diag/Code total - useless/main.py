#-------------------------------------------------------------------
# IMPORT DES LIBRAIRIES
#-------------------------------------------------------------------
import sys
import pyvisa
from srfd_lib import amp
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QHBoxLayout, QCheckBox, QLineEdit,
    QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QComboBox, QTextEdit , QMessageBox
from PyQt5.QtGui import QIntValidator
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
GE_LIGHT_PURPLE = "#F5F0FA"


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
# Classe step
#-------------------------------------------------------------------
class Step(QWidget):
    def __init__(self, titre, image_path, next_callback, back_callback=None, security=False, first_step=False):
        super().__init__()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(GE_LIGHT_PURPLE))
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
# classe mainwindow + IHM
#-------------------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow GE Healthcare")
        self.resize(900, 700)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(GE_LIGHT_PURPLE))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        rm_rs232 = pyvisa.ResourceManager('@py')
        self.srfd_com = rm_rs232.open_resource("ASRL6::INSTR")
        self.srfd_com.baud_rate = 9600
        self.srfd_com.data_bits = 8
        self.srfd_com.stop_bits = pyvisa.constants.StopBits.one
        self.srfd_com.parity = pyvisa.constants.Parity.none
        self.srfd_com.timeout = 5000

        self.srfd_amp_master = rm_rs232.open_resource("ASRL8::INSTR")
        self.srfd_amp_master.baud_rate = 9600
        self.srfd_amp_master.data_bits = 8
        self.srfd_amp_master.stop_bits = pyvisa.constants.StopBits.one
        self.srfd_amp_master.parity = pyvisa.constants.Parity.none
        self.srfd_amp_master.timeout = 5000

        self.srfd_amp_slave = rm_rs232.open_resource("ASRL7::INSTR")
        self.srfd_amp_slave.baud_rate = 9600
        self.srfd_amp_slave.data_bits = 8
        self.srfd_amp_slave.stop_bits = pyvisa.constants.StopBits.one
        self.srfd_amp_slave.parity = pyvisa.constants.Parity.none
        self.srfd_amp_slave.timeout = 5000

        self.user_info = {}

        # --- créer le QStackedWidget AVANT de l'utiliser ---
        self.stack = QStackedWidget()

        # --- maintenant tu peux ajouter des pages ---
        self.stack.addWidget(LoginPage(self.next_step))

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)


        # -------------------
        # Pages d’intro
        # -------------------
        self.stack.addWidget(TransitionPage("On va commencer le process de diagnostique de l'amplificateur 1.5T - Banc 0 - ", self.next_step, first=True))
        self.add_step("AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V", "Cabinet_alim.png", security=True)
        self.stack.addWidget(TransitionPage("Partie 1 du process :\nCâblage COM", self.next_step, image_path="COM.png"))
        # -------------------
        # IHM 1 : Câblage COM
        # -------------------
        self.add_step("Câblage COM - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Câblage COM - Étape 2 : Identifier  l'amplificateur avant de l'utiliser / l'installer", "Amplifier.png", first_step=True)
        self.add_step("Câblage COM - Étape 3 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage COM - Étape 4 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage COM - Étape 5 : Résultat", "Amplificateur_ouvert.png")
        self.add_step("Câblage COM - Étape 6 : Brancher le câble de COM sur l'amplificateur du haut", "Master_connection.png")
        self.add_step("Câblage COM - Étape 7 : Brancher le câble de COM sur l'amplificateur du bas", "Slave_connection.png")

        # Transition vers IHM 2
        self.stack.addWidget(TransitionPage("Partie 2 du process :\nAlimentation", self.next_step, image_path="Alimentation.png"))

        # -------------------
        # IHM 2 : Alimentation
        # -------------------
        self.add_step("Alimentation - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Alimentation - Étape 2 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Alimentation - Étape 3 : Vérifier et mettre les équipements de protection individuels", "EPI.png")
        self.add_step("Alimentation - Étape 4 : Tester l'appareil avant de l'utiliser", "VAT_Test.png")
        self.add_step("Alimentation - Étape 5 : Vérification de l'absence de tension", "VAT_Verification.png")
        self.add_step("Alimentation - Étape 6 : Lier l'amplificateur et le PDU à travers le câble d'alimentation", "Triphase.png", security=True)
        self.add_step("Alimentation - Étape 7 : Mettre la vitre isolante pour plus de protection", "Vitre_isolante.png")

        # Transition vers IHM 3
        self.stack.addWidget(TransitionPage("Partie 3 du process :\nMise en marche", self.next_step, image_path="Mise_en_marche.png"))

        # -------------------
        # IHM 3 : Mise en marche
        # -------------------
        self.add_step("Fonctionnement - Étape 1 : Mettre le banc en mode fonctionnement", "Etat_ON.png")
        self.add_step("Fonctionnement - Étape 2 : Activer le disjoncteur de l'amplificateur", "Disjoncteur_amplificateur.png")
        self.add_step("Fonctionnement - Étape 3 : Information importante | Sécurité", "Security.png", security=True)

        # IHM finale : Mesure
        self.stack.addWidget(MeasurePage(self.srfd_com, self.srfd_amp_master, self.srfd_amp_slave))

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)

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


# ---------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------
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
        writer.writerow(["Résultats LNA", ""])

        for line in output_list:
            writer.writerow([line, ""])

    # Excel
    xlsx_filename = base + ".xlsx"

    df_user = pd.DataFrame(list(user_info.items()), columns=["Champ", "Valeur"])
    df_results = pd.DataFrame({"Résultats": output_list})

    with pd.ExcelWriter(xlsx_filename, engine="xlsxwriter") as writer:
        df_user.to_excel(writer, sheet_name="User Info", index=False)
        df_results.to_excel(writer, sheet_name="Results", index=False)

        workbook = writer.book
        worksheet = writer.sheets["User Info"]

        try:
            worksheet.insert_image("D2", "Pics/GE_Logo.png", {"x_scale": 0.5, "y_scale": 0.5})
        except:
            pass

    return csv_filename, xlsx_filename

#-------------------------------------------------------------------
# Classe mesure + export PDF des résultats
#-------------------------------------------------------------------
class MeasurePage(QWidget):
    def __init__(self, srfd_com, srfd_amp_master, srfd_amp_slave):
        super().__init__()
        layout = QVBoxLayout()

        self.combo = QComboBox()
        self.combo.addItems(["Amplificateur Master", "Amplificateur Slave"])
        layout.addWidget(self.combo)

        self.result_display = QTextEdit()
        self.loading_label = QLabel("Chargement des mesures…")
        self.loading_label.setStyleSheet("""
            QLabel {
                background-color: #4B0082;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 8px;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        btn = QPushButton("Mesure")
        btn.setFont(QFont("Arial", 12, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #4B0082; 
                color: white; 
                padding: 12px 30px; 
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5C1AA3;
            }
        """)
        # ✅ Connexion du bouton à la fonction run_measure
        btn.clicked.connect(lambda: self.run_measure(srfd_com, srfd_amp_master, srfd_amp_slave))
        layout.addWidget(btn)
        self.setLayout(layout)


    def safe_read_lines(self, instr, expected_lines):
        lines = []
        try:
            for _ in range(expected_lines):
                line = instr.read()
                lines.append(line.replace('\r', '').replace('\n', ''))
        except Exception:
            ... 
        return lines
    
    def read_until_timeout(self, instr):
        lines = []
        while True:
            try:
                line = instr.read()
                #line = line.replace('\r', '').replace('\n', '')
                if line.strip():
                    lines.append(line.replace('\r', '').replace('\n', ''))
            except Exception:
                break   # timeout = fin de transmission
        return lines


    def run_measure(self, srfd_com, srfd_amp_master, srfd_amp_slave):
        amp_choice = self.combo.currentText()
        srfd_amp = srfd_amp_master if "Master" in amp_choice else srfd_amp_slave
        output = []
        self.loading_label.show()
        QApplication.processEvents()

        try:
            # --- Étapes communes ---
            output.append("Etape 1 : Mise en power off...")
            amp.poweroff(srfd_com)
            state, wait = amp.check_amp_state(srfd_com)
            output.append(f"📊 Registre 0x3011: state={state}, wait={wait}")

            output.append("⚠️ Fault: " + amp.srfd_write(srfd_amp, "FAULT?\n"))
            amp.srfd_write(srfd_amp, "MEAS?")
            output.append("📈 Meas : " + srfd_amp.read())
            output.append("🧭 Mode: " + amp.srfd_write(srfd_amp, "MODE?\n"))

            output.append("Etape 2 : Passage en standby...")
            amp.standby(srfd_com)
            state, wait = amp.check_amp_state(srfd_com)
            output.append(f"📊 Registre 0x3011: state={state}, wait={wait}")

            output.append("⚠️ Fault: " + amp.srfd_write(srfd_amp, "FAULT?\n"))
            amp.srfd_write(srfd_amp, "MEAS?")
            output.append("📈 Meas : " + srfd_amp.read())
            output.append("🧭 Mode: " + amp.srfd_write(srfd_amp, "MODE?\n"))

            # --- Diagnostic Master ---
            if "Master" in amp_choice:
                output.append("\n")
                output.append("---- START OF AMP DIAGNOSTIC (Master) ----")
                output.append("\n")

                output.append("-------------------------- DAC registers (Master) ---------------------------")
                output.append("\n")
                amp.amp_password(srfd_amp_master)
                srfd_amp_master.write("DAC? *")
                srfd_amp_master.read()
                output.extend(self.read_until_timeout(srfd_amp_master))
                output.append("\n")

            if "Master" in amp_choice:
                output.append("\n")
                output.append("------------------------- Biasing registers (Master) ------------------------")
                output.append("\n")
                srfd_amp_master.write("BIAS:MEAS? 0")
                srfd_amp_master.read()
                output.extend(self.safe_read_lines(srfd_amp_master, 11))
                output.append("\n")
                output.append("------------------------- END OF AMP DIAGNOSTIC (Master) ------------------\n")
                
                output.append("Etape 3 : Retour en power off...")
                amp.poweroff(srfd_com)
                state, wait = amp.check_amp_state(srfd_com)
                output.append(f"📊 Registre 0x3011: state={state}, wait={wait}")
                output.append("\n")

            # --- Diagnostic Slave ---
            
            if "Slave" in amp_choice:
                output.append("\n")
                output.append("---- START OF AMP DIAGNOSTIC (Slave) ----")
                output.append("\n")

                output.append("-------------------------- DAC registers (Slave) ---------------------------")
                output.append("\n")
                amp.amp_password(srfd_amp_slave)
                srfd_amp_slave.write("DAC? *")
                srfd_amp_slave.read()
                output.extend(self.read_until_timeout(srfd_amp_slave))
                output.append("\n")

            if "Slave" in amp_choice:
                output.append("\n")
                output.append("------------------------- Biasing registers (Slave) ------------------------")
                output.append("\n")
                srfd_amp_slave.write("BIAS:MEAS? 0")
                srfd_amp_slave.read()
                output.extend(self.safe_read_lines(srfd_amp_slave, 11))
                output.append("\n")
                output.append("------------------------- END OF AMP DIAGNOSTIC (Slave) ------------------\n")

                output.append("Etape 3 : Retour en power off...")
                amp.poweroff(srfd_com)
                state, wait = amp.check_amp_state(srfd_com)
                output.append(f"📊 Registre 0x3011: state={state}, wait={wait}")
                output.append("\n")

        except Exception as e:
            output.append(f"❌ Erreur: {str(e)}")

        self.loading_label.hide()
        self.result_display.setText("\n".join(output))
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SRFD_Report_{ts}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Logo
        story.append(Image("Pics/GE_Logo.png", width=80, height=80))
        story.append(Spacer(1, 20))

        # Infos utilisateur
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

        # Résultats mesures
        story.append(Paragraph("<b>Résultats Mesures</b>", styles["Heading2"]))
        for line in output:
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)
        self.result_display.append(f"\n✅ Export PDF effectué : {filename}")
        csv_file, xlsx_file = export_results(output, user, ts)
        self.result_display.append(f"Export CSV effectué : {csv_file}")
        self.result_display.append(f"Export Excel effectué : {xlsx_file}")



#-------------------------------------------------------------------
# Main
#-------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


#-------------------------------------------------------------------
# Fin du programme
#-------------------------------------------------------------------