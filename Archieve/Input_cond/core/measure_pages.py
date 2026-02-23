import shutil
import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QApplication
from PyQt5.QtGui import QFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from Input_cond.core.export_utils import export_results
from Input_cond.core.error_handler import ERROR_HINTS


class MeasureBodyPage(QWidget):
    def __init__(self, scope, swg33522B, swg33611A, srfd_com, next_callback):
        super().__init__()
        self.scope = scope
        self.swg33522B = swg33522B
        self.swg33611A = swg33611A
        self.srfd_com = srfd_com
        self.next_callback = next_callback

        layout = QVBoxLayout()
        title = QLabel("Mesure BODY")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        btn = QPushButton("Lancer mesure BODY")
        btn.setStyleSheet("background-color:#4B0082; color:white; padding:8px;")
        btn.clicked.connect(self.run_measure)
        layout.addWidget(btn)

        self.setLayout(layout)

    def run_measure(self):
        output = []
        self.result_display.clear()
        QApplication.processEvents()

        error_code = "00"
        output.append("Étape 1 : Vérification de l'état de l'amplificateur (simulation)…")
        output.append(f"Erreur brute (0x3014) : {error_code}")
        output.append(f"ℹ️ Indice : {ERROR_HINTS.get(error_code, 'Erreur inconnue.')}")

        output.append("Étape 2 : Configuration des instruments (simulation)…")

        power_minus20 = 50.0
        output.append("Étape 3 : Mesure -20 dBm (simulation)…")
        output.append(f"Puissance BODY : {power_minus20:.2f} dBm")

        power_gain = 72.0
        output.append("Étape 4 : Mesure 0 dBm (simulation)…")
        output.append(f"Puissance BODY (gain) : {power_gain:.2f} dBm")

        self.result_display.setText("\n".join(output))
        self.parent().parent().body_results = "\n".join(output)
        self.next_callback()



class MeasureHeadPage(QWidget):
    def __init__(self, scope, swg33522B, swg33611A, srfd_com, next_callback=None):
        super().__init__()
        self.scope = scope
        self.swg33522B = swg33522B
        self.swg33611A = swg33611A
        self.srfd_com = srfd_com
        self.next_callback = next_callback

        layout = QVBoxLayout()
        title = QLabel("Mesure HEAD")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        btn = QPushButton("Lancer mesure HEAD")
        btn.setStyleSheet("background-color:#4B0082; color:white; padding:8px;")
        btn.clicked.connect(self.run_measure)
        layout.addWidget(btn)

        self.setLayout(layout)

    def run_measure(self):
        output = []
        self.result_display.clear()
        QApplication.processEvents()

        error_code = "00"
        output.append("Étape 1 : Vérification de l'état de l'amplificateur (simulation)…")
        output.append(f"Erreur brute (0x3014) : {error_code}")
        output.append(f"ℹ️ Indice : {ERROR_HINTS.get(error_code, 'Erreur inconnue.')}")

        output.append("Étape 2 : Configuration des instruments (simulation)…")

        power_head = 63.0
        output.append("Étape 3 : Mesure HEAD (simulation)…")
        output.append(f"Puissance HEAD : {power_head:.2f} dBm")

        self.result_display.setText("\n".join(output))

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SRFD_InputGain_Report_{ts}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Image("Pics/GE_Logo.png", width=80, height=80))
        story.append(Spacer(1, 16))

        user = self.parent().parent().user_info
        story.append(Paragraph("<b>Rapport Utilisateur</b>", styles["Heading3"]))
        story.append(Paragraph(f"SSO: {user.get('SSO','')}", styles["Normal"]))
        story.append(Paragraph(f"Nom: {user.get('Nom','')}", styles["Normal"]))
        story.append(Paragraph(f"Prénom: {user.get('Prenom','')}", styles["Normal"]))
        story.append(Paragraph(f"Atelier: {user.get('Atelier','')}", styles["Normal"]))
        story.append(Paragraph(f"DUT Serial Number: {user.get('DUT_Serial','')}", styles["Normal"]))
        story.append(Paragraph(f"Part Number: {user.get('Part_Number','')}", styles["Normal"]))
        story.append(Paragraph(f"PN Revision: {user.get('PN_Revision','')}", styles["Normal"]))
        story.append(Paragraph(f"Test Date: {user.get('Test_Date','')}", styles["Normal"]))
        story.append(Paragraph(f"Station ID: {user.get('Station_ID','')}", styles["Normal"]))
        story.append(Spacer(1, 16))

        body = getattr(self.parent().parent(), "body_results", None)
        if body:
            story.append(Paragraph("<b>Résultats BODY</b>", styles["Heading3"]))
            for line in body.split("\n"):
                story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 12))

        story.append(Paragraph("<b>Résultats HEAD</b>", styles["Heading3"]))
        for line in self.result_display.toPlainText().split("\n"):
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)
        self.result_display.append(f"\n✅ Export PDF effectué : {filename}")

        output_list = []
        if body:
            for line in body.split("\n"):
                output_list.append("BODY: " + line)
        for line in self.result_display.toPlainText().split("\n"):
            output_list.append("HEAD: " + line)

        csv_file = export_results(output_list, user, ts)
        network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

        try:
            shutil.copy(csv_file, network_path)
            self.result_display.append("📤 CSV envoyé sur EDHR.")
        except Exception as e:
            self.result_display.append(f"❌ Erreur envoi EDHR : {e}")

        self.result_display.append(f"✅ Export CSV effectué : {csv_file}")

        if self.next_callback:
            self.next_callback()
