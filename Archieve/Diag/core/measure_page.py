from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import datetime
from Diag.core.export_utils import export_results
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        output = []

        self.loading_label.show()
        QApplication.processEvents()

        try:
            output.append("Etape 1 : Mise en power off (simulation)...")

            output.append("📊 Registre 0x3011: state=power off, wait=0 (simulation)")
            output.append("⚠️ Fault (FAULT?) : 0 (simulation)")

            error_code = "00"
            output.append(f"Erreur brute (0x3014) : {error_code}")
            output.append("ℹ️ Indice : Aucun défaut détecté (simulation)")

            output.append("📈 Meas : 123.4 (simulation)")
            output.append("🧭 Mode: BODY (simulation)")

            output.append("Etape 2 : Passage en standby (simulation)...")
            output.append("📊 Registre 0x3011: state=standby, wait=0 (simulation)")
            output.append("⚠️ Fault (FAULT?) : 0 (simulation)")

            output.append("📈 Meas : 123.4 (simulation)")
            output.append("🧭 Mode: BODY (simulation)")

            if "Master" in amp_choice:
                output.append("")
                output.append("---- START OF AMP DIAGNOSTIC (Master) ----")
                output.append("")
                output.append("-------------------------- DAC registers (Master) ---------------------------")
                output.append("")
                output.append("DAC0: 1000 (simulation)")
                output.append("DAC1: 1000 (simulation)")
                output.append("")
                output.append("------------------------- Biasing registers (Master) ------------------------")
                output.append("")
                output.append("BIAS0: 1.23 A (simulation)")
                output.append("BIAS1: 1.23 A (simulation)")
                output.append("")
                output.append("------------------------- END OF AMP DIAGNOSTIC (Master) ------------------")
                output.append("")
                output.append("Etape 3 : Retour en power off (simulation)...")
                output.append("📊 Registre 0x3011: state=power off, wait=0 (simulation)")

            if "Slave" in amp_choice:
                output.append("")
                output.append("---- START OF AMP DIAGNOSTIC (Slave) ----")
                output.append("")
                output.append("-------------------------- DAC registers (Slave) ---------------------------")
                output.append("")
                output.append("DAC0: 1000 (simulation)")
                output.append("DAC1: 1000 (simulation)")
                output.append("")
                output.append("------------------------- Biasing registers (Slave) ------------------------")
                output.append("")
                output.append("BIAS0: 1.23 A (simulation)")
                output.append("BIAS1: 1.23 A (simulation)")
                output.append("")
                output.append("------------------------- END OF AMP DIAGNOSTIC (Slave) ------------------")
                output.append("")
                output.append("Etape 3 : Retour en power off (simulation)...")
                output.append("📊 Registre 0x3011: state=power off, wait=0 (simulation)")

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
        story.append(Image(os.path.join(BASE_DIR, "Pics", "GE_Logo.png"), width=80, height=80))
        story.append(Spacer(1, 20))

        # Infos utilisateur
        user = self.parent().parent().user_info
        story.append(Paragraph("<b>Rapport Utilisateur</b>", styles["Heading2"]))
        story.append(Paragraph(f"SSO: {user['SSO']}", styles["Normal"]))
        story.append(Paragraph(f"Nom: {user['Nom']}", styles["Normal"]))
        story.append(Paragraph(f"Prénom: {user['Prenom']}", styles["Normal"]))
        story.append(Paragraph(f"Atelier: {user['Atelier']}", styles["Normal"]))
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
        csv_file = export_results(output, user, ts)
        self.result_display.append(f"✅ Export CSV effectué : {csv_file}")
