from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from Performance_burning.SCOPE_MEAS.core_scope.export_scope import export_results_scope
import shutil


GE_PURPLE = "#4B0082"

class MeasurePageScope(QWidget):
    def __init__(self, scope, swg33522B, swg33611A, srfd_com):
        super().__init__()
        self.scope = scope
        self.swg33522B = swg33522B
        self.swg33611A = swg33611A
        self.srfd_com = srfd_com

        layout = QVBoxLayout()

        title = QLabel("Mesure SCOPE – Single pulse / Harmoniques / Intermod")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color:{GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        btn = QPushButton("Lancer la séquence de mesures")
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
        btn.clicked.connect(self.run_measure)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def run_measure(self):
        self.result_display.clear()
        try:
            self.result_display.append("🔌 Mise en power off de l'ampli (simulation)...")
            QApplication.processEvents()

            error_code = "00"
            decoded = "Aucun défaut détecté (simulation)"
            self.result_display.append(f"Erreur brute (0x3014) : {error_code}")
            self.result_display.append(f"Erreur décodée : {decoded}")

            self.result_display.append("▶ Lancement des mesures SCOPE (simulation)...")
            QApplication.processEvents()

            gain_variation = 0.2
            output_power = 55.0
            harmonic_output = 35.0
            intermodulation = 12.0

            self.result_display.append("")
            self.result_display.append(f"📡 Puissance de sortie : {round(output_power, 2)} dBm")
            self.result_display.append("")

            self.result_display.append(
                f"Single pulse drop : {round(gain_variation, 2)} dB "
                + ("(< 0.35 dB, in spec)" if gain_variation < 0.35 else "(> 0.35 dB, out of spec)")
            )

            self.result_display.append(
                f"Harmonic output : {round(harmonic_output, 2)} dB "
                + (">(30 dB, in spec)" if harmonic_output > 30 else "(< 30 dB, out of spec)")
            )

            self.result_display.append(
                f"Intermodulation : {round(intermodulation, 2)} dB "
                + (">(10 dB, in spec)" if intermodulation > 10 else "(< 10 dB, out of spec)")
            )

        except Exception as e:
            QMessageBox.critical(self, "Erreur mesure", str(e))
        finally:
            self.result_display.append("\n🔌 Mise en power off finale de l'ampli (simulation).")
            QApplication.processEvents()

            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"SRFD_SCOPE_Report_{ts}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            story.append(Image("assets/Pics/GE_Logo.png", width=80, height=80))
            story.append(Spacer(1, 16))

            # Infos utilisateur
            user = self.parent().parent().user_info
            story.append(Paragraph("<b>Rapport Utilisateur</b>", styles["Heading3"]))
            story.append(Paragraph(f"SSO: {user.get('SSO','')}", styles["Normal"]))
            story.append(Paragraph(f"Nom: {user.get('Nom','')}", styles["Normal"]))
            story.append(Paragraph(f"Prénom: {user.get('Prenom','')}", styles["Normal"]))
            story.append(Paragraph(f"Atelier: {user.get('Departement','')}", styles["Normal"]))
            story.append(Paragraph(f"DUT Serial Number: {user.get('DUT_Serial','')}", styles["Normal"]))
            story.append(Paragraph(f"Part Number: {user.get('Part_Number','')}", styles["Normal"]))
            story.append(Paragraph(f"PN Revision: {user.get('PN_Revision','')}", styles["Normal"]))
            story.append(Paragraph(f"Test Date: {user.get('Test_Date','')}", styles["Normal"]))
            story.append(Paragraph(f"Station ID: {user.get('Station_ID','')}", styles["Normal"]))
            story.append(Spacer(1, 16))

        # Résultats scope 

            story.append(Paragraph("<b>Résultats SCOPE</b>", styles["Heading3"]))
            for line in self.result_display.toPlainText().split("\n"):
                story.append(Paragraph(line, styles["Normal"]))

            doc.build(story)
            self.result_display.append(f"\n✅ PDF généré : {filename}")

            output_list = ["SCOPE: " + line for line in self.result_display.toPlainText().split("\n")]

            csv_file = export_results_scope(output_list, user, ts)

            network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

            try:
                shutil.copy(csv_file, network_path)
                self.result_display.append("📤 CSV envoyé sur EDHR.")
            except Exception as e:
                self.result_display.append(f"❌ Erreur envoi EDHR : {e}")

            self.result_display.append(f"✅ CSV généré : {csv_file}")
