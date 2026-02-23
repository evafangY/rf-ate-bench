# -------------------------
# Bibliothèques
# -------------------------
import sys
import pyvisa
import time
import math
import numpy
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QHBoxLayout, QCheckBox, QLineEdit,
    QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QSize
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import csv
import pandas as pd
from reportlab.lib.utils import ImageReader


from Libraries.srfd_lna_lib import (
    config_rf_swg,
    config_scope_spectrum,
    config_lna_psu,
    config_amp_channels,
    poweroff,
    standby,
    operate,
    power_off_system_33611A,
    RBW_HZ
)

# Couleurs
GE_PURPLE = "#4B0082"
#GE_LIGHT_PURPLE = "#F5F0FA"


# -------------------------
# Login Page
# -------------------------
# -------------------------
# Login Page
# -------------------------
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


# -------------------------
# Step Page
# -------------------------
class Step(QWidget):
    def __init__(self, titre, image_path, next_callback, back_callback=None, security=False, first_step=False):
        super().__init__()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Titre + logo
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

        # Retour
        if back_callback and not first_step:
            back_btn = QPushButton("Retour")
            back_btn.clicked.connect(back_callback)
            btn_layout.addWidget(back_btn)

        # Défaut
        defaut_btn = QPushButton("Défaut")
        defaut_btn.clicked.connect(self.mark_defaut)
        btn_layout.addWidget(defaut_btn)

        # Fait
        fait_btn = QPushButton("Fait")
        fait_btn.clicked.connect(self.mark_done)
        btn_layout.addWidget(fait_btn)

        # Valider
        if security:
            self.checkbox = QCheckBox("J'ai pris connaissance de l'information")
            layout.addWidget(self.checkbox)

            validate_btn = QPushButton("Valider")
            validate_btn.setEnabled(False)

            def toggle_btn():
                validate_btn.setEnabled(self.checkbox.isChecked())

            self.checkbox.stateChanged.connect(toggle_btn)
            validate_btn.clicked.connect(lambda: self.try_next(next_callback))
            btn_layout.addWidget(validate_btn)

        else:
            btn = QPushButton("Valider")
            btn.clicked.connect(lambda: self.try_next(next_callback))
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def mark_defaut(self):
        self.defaut = True
        self.done = False
        QMessageBox.warning(self, "Étape en défaut","Cette étape est en défaut.\nImpossible de passer tant que ce n'est pas corrigé.")

    def mark_done(self):
        self.done = True
        self.defaut = False

    def try_next(self, next_callback):
        if self.done and not self.defaut:
            next_callback()
        else:
            QMessageBox.warning(self, "Validation requise","Vous devez cliquer sur 'Fait' avant de valider.")


# -------------------------
# Transition Page
# -------------------------
class TransitionPage(QWidget):
    def __init__(self, message, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel(message)
        label.setFont(QFont("Arial", 32 if first else 26, QFont.Bold))
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
            layout.addWidget(img_label)

        btn = QPushButton("Suivant")
        btn.clicked.connect(next_callback)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

# ---------------------------------------------------------
# MainWindow – Workflow complet
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workflow GE Healthcare")
        self.resize(900, 700)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.user_info = {}

        # Stack
        self.stack = QStackedWidget()
        self.stack.addWidget(LoginPage(self.next_step))

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # -------------------
        # Pages d’intro
        # -------------------
        self.stack.addWidget(TransitionPage(
            "On va commencer le process de diagnostique de l'amplificateur 1.5T - Banc 0 - ",
            self.next_step,
            first=True
        ))

        self.add_step("AVERTISSEMENT :\n\nLa tension est TOUJOURS présente en haut du banc\nvu qu'il est toujours lié au boitier externe de l'alimentation 240V",
                      "Cabinet_alim.png", security=True)

        self.stack.addWidget(TransitionPage("Partie 1 du process :\nCâblage COM", self.next_step, image_path="COM.png"))

        # -------------------
        # IHM 1 : Câblage COM
        # -------------------
        self.add_step("Câblage COM - Étape 1 : Vérification de l'unité d'alimentation du banc", "PDU.png")
        self.add_step("Câblage COM - Étape 2 : Identifier l'amplificateur avant de l'utiliser / l'installer", "Amplifier.png", first_step=True)
        self.add_step("Câblage COM - Étape 3 : Prendre un tournevis isolant PH1 (double triangle)", "Tournevice.png")
        self.add_step("Câblage COM - Étape 4 : Enlever le capot de l'amplificateur", "Capot.png")
        self.add_step("Câblage COM - Étape 5 : Résultat", "Amplificateur_ouvert.png")
        self.add_step("Câblage COM - Étape 6 : Effectuer le câblage suivant pour le LNA", "Cablage_blanking.png")
        self.add_step("Câblage COM - Étape 7 : Effectuer le câblage suivant pour la communication", "Cablage_COM_Blanking.png")

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


        # Transition vers IHM 4
        self.stack.addWidget(TransitionPage("Partie 4 du process :\nMesure de bruit", self.next_step, image_path="Noise.png"))

        # -------------------
        # IHM 4 : Mesure de bruit
        # -------------------
        self.stack.addWidget(MeasurePage_LNA())

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


# ---------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------
def export_results(output_list, user_info, timestamp):
    base = f"LNA_Report_{timestamp}"

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

# ---------------------------------------------------------
# MeasurePage – Intégration du code LNA
# ---------------------------------------------------------
class MeasurePage_LNA(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Mesure LNA – Bruit Blanked")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Zone résultats
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # Label chargement
        self.loading_label = QLabel("Chargement…")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                background-color: #4B0082;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        # Bouton mesure
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
        btn.clicked.connect(self.run_measure)
        layout.addWidget(btn)

        self.setLayout(layout)

    # ---------------------------------------------------------
    # Code LNA intégré proprement
    # ---------------------------------------------------------
    def run_measure(self):
        self.loading_label.show()
        QApplication.processEvents()

        output = []

        try:
            # Initialisation VISA
            output.append("Initialisation des instruments…")
            rm = pyvisa.ResourceManager()

            swg33611A = rm.open_resource("USB0::0x0957::0x4807::MY59003502::0::INSTR")
            swg33611A.timeout = 5000

            scope = rm.open_resource("USB0::0x0AAD::0x0197::1335.2050k04-101598::0::INSTR")
            scope.timeout = 5000

            psu = rm.open_resource("ASRL5::INSTR")
            psu.timeout = 5000

            rm_rs232 = pyvisa.ResourceManager('@py')
            srfd_com = config_amp_channels(rm_rs232)

            # Setup ampli
            output.append("Mise en power off…")
            poweroff(srfd_com)

            output.append("Passage en standby…")
            standby(srfd_com)

            output.append("Passage en operate…")
            operate(srfd_com)

            # Setup banc
            output.append("Configuration PSU…")
            config_lna_psu(psu)

            output.append("Configuration RF SWG…")
            config_rf_swg(swg33611A, dBm=-20)

            output.append("Configuration oscilloscope…")
            config_scope_spectrum(scope)

            time.sleep(1)

            # Mesure bruit
            output.append("Mesure du bruit…")
            scope.write("FORM ASC")
            scope.write("CALCulate:SPECtrum1:WAVeform:NORMal:DATA:VALues?")
            raw_fft = scope.read()
            data_fft = [float(val) for val in raw_fft.strip().split(',')]
            fft_data_array = numpy.array(data_fft)

            random_noise = numpy.average(fft_data_array) - 10 * math.log10(RBW_HZ) - 30
            coherent_noise = numpy.max(fft_data_array) - 10 * math.log10(RBW_HZ) - 30

            output.append(f"Bruit random (dBm/Hz) : {random_noise:.2f}")
            output.append(f"Bruit coherent (dBm/Hz) : {coherent_noise:.2f}")

            # Shutdown
            output.append("Arrêt du système…")
            power_off_system_33611A(swg33611A, psu, srfd_com)

        except Exception as e:
            output.append(f"Erreur : {str(e)}")

        self.loading_label.hide()
        self.result_display.setText("\n".join(output))

        # Export PDF
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"LNA_Report_{ts}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

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

        # Résultats
        story.append(Paragraph("<b>Résultats Mesure LNA</b>", styles["Heading2"]))
        for line in output:
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)
        self.result_display.append(f"\nExport PDF effectué : {filename}")

        csv_file, xlsx_file = export_results(output, user, ts)
        self.result_display.append(f"Export CSV effectué : {csv_file}")
        self.result_display.append(f"Export Excel effectué : {xlsx_file}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

#-------------------------------------------------------------------
# Fin du programme
#-------------------------------------------------------------------