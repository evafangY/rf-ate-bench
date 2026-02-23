from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import time
from Noise_meas.Blanked.core_blanked.export_utils_blanked import export_results
import shutil

GE_PURPLE = "#4B0082"

class MeasurePage_LNA(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        t = QLabel("Mesure LNA – Bruit Blanked")
        t.setFont(QFont("Arial", 18, QFont.Bold))
        t.setStyleSheet(f"color:{GE_PURPLE};")
        layout.addWidget(t)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.loading_label = QLabel("Chargement…")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        b = QPushButton("Mesure")
        b.clicked.connect(self.run_measure)
        layout.addWidget(b)

        self.setLayout(layout)

    def run_measure(self):
        self.loading_label.show()
        QApplication.processEvents()

        output = []

        output.append("Initialisation des instruments (simulation)…")
        output.append("Mise en power off (simulation)…")

        error_code = "00"
        output.append(f"Erreur brute (0x3014) : {error_code}")
        output.append("Erreur décodée : Aucun défaut détecté (simulation)")

        output.append("Passage en standby (simulation)…")
        output.append("Passage en operate (simulation)…")
        output.append("Configuration PSU (simulation)…")
        output.append("Configuration RF SWG (simulation)…")
        output.append("Configuration oscilloscope (simulation)…")

        time.sleep(1)

        random_noise = -160.0
        coherent_noise = -150.0

        output.append(f"Bruit random (dBm/Hz) : {random_noise:.2f}")
        output.append(f"Bruit coherent (dBm/Hz) : {coherent_noise:.2f}")

        self.loading_label.hide()
        self.result_display.setText("\n".join(output))

        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"LNA_Report_{ts}.pdf"

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
        story.append(Paragraph(f"Atelier: {user['Departement']}", styles["Normal"]))
        story.append(Paragraph(f"DUT Serial Number: {user['DUT_Serial']}", styles["Normal"]))
        story.append(Paragraph(f"Part Number: {user['Part_Number']}", styles["Normal"]))
        story.append(Paragraph(f"PN Revision: {user['PN_Revision']}", styles["Normal"]))
        story.append(Paragraph(f"Test Date: {user['Test_Date']}", styles["Normal"]))
        story.append(Paragraph(f"Station ID: {user['Station_ID']}", styles["Normal"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Résultats Mesure LNA</b>", styles["Heading2"]))

        for line in output:
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)

        csv_file = export_results(output, user, ts)

        network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

        try:
            shutil.copy(csv_file, network_path)
            self.result_display.append("📤 CSV envoyé sur EDHR.")
        except Exception as e:
            self.result_display.append(f"❌ Erreur envoi EDHR : {e}")

        self.result_display.append(f"CSV: {csv_file}")

