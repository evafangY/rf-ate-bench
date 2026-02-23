from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from Performance_burning.VNA_MEAS.core_vna.export_vna import export_results
import shutil


GE_PURPLE = "#4B0082"

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
            vswr = 1.05
            flatness = 0.3
            gain_stab = 0.1
            phase_stab = 1.5

            self.out.append("Simulation de mesure VNA")
            self.out.append(f"Gain flatness: {round(flatness, 2)} dB")
            self.out.append(f"VSWR: {round(vswr, 2)} :1")
            self.out.append(f"Interpulse gain stability: {round(gain_stab, 2)} dB")
            self.out.append(f"Interpulse phase stability: {round(phase_stab, 2)} °")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
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

            network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

            try:
                shutil.copy(csv_file, network_path)
                self.out.append("📤 CSV envoyé sur EDHR.")
            except Exception as e:
                self.out.append(f"❌ Erreur envoi EDHR : {e}")

            self.out.append(f"Export CSV effectué : {csv_file}")
