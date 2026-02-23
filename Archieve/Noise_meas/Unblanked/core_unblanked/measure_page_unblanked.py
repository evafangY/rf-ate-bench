from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import time
from Noise_meas.Unblanked.core_unblanked.export_utils_unblanked import export_results
import shutil



GE_PURPLE = "#4B0082"
LIMIT_UNBLANKED = -70

class MeasurePage_UNBLANKED(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("Mesure LNA – Bruit UNBLANKED")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.loading_label = QLabel("Chargement…")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        btn = QPushButton("Mesure")
        btn.clicked.connect(self.run_measure)
        layout.addWidget(btn)

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
        output.append("Configuration générateur BLANKING/UNBLANKING (simulation)…")
        output.append("Configuration oscilloscope (simulation)…")

        time.sleep(1)

        val_dBm = -120.0
        val_dBmHz = -150.0

        output.append(f"Bruit mesuré (dBm) : {val_dBm:.2f}")
        output.append(f"Bruit corrigé (dBm/Hz) : {val_dBmHz:.2f}")
        output.append(f"UNBLANKED PASS ? {val_dBmHz < LIMIT_UNBLANKED}")

        self.loading_label.hide()
        self.result_display.setText("\n".join(output))

        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"LNA_Unblanked_Report_{ts}.pdf"
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

        story.append(Paragraph("<b>Résultats Mesure LNA UNBLANKED</b>", styles["Heading2"]))
        for line in output:
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)
        self.result_display.append(f"\nExport PDF effectué : {filename}")
        csv_file = export_results(output, user, ts)

        network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

        try:
            shutil.copy(csv_file, network_path)
            self.result_display.append("📤 CSV envoyé sur EDHR.")
        except Exception as e:
            self.result_display.append(f"❌ Erreur envoi EDHR : {e}")


        self.result_display.append(f"Export CSV effectué : {csv_file}")
    
