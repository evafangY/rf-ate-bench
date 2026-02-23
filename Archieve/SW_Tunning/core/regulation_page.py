from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication
from PyQt5.QtGui import QFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from PyQt5.QtCore import Qt, QSize
from reportlab.lib.styles import getSampleStyleSheet
import datetime, time
from SW_Tunning.core.export_utils import export_results
import shutil
import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GE_PURPLE = "#4B0082"

class RegulationPage(QWidget):
    def __init__(self, scope, srfd_com, srfd_amp_master, srfd_amp_slave, next_callback, swg33522B, swg33611A):
        super().__init__()
        self.scope = scope
        self.srfd_com = srfd_com
        self.srfd_amp_master = srfd_amp_master
        self.srfd_amp_slave = srfd_amp_slave
        self.swg33522B = swg33522B 
        self.swg33611A = swg33611A

        layout = QVBoxLayout()

        title = QLabel("Régulation automatique du gain")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet(f"color:{GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        btn_master = QPushButton("Réguler Master")
        btn_master.clicked.connect(lambda: self.run_regulation(self.srfd_amp_master, "MEASurement1:RESult:ACTual?"))
        layout.addWidget(btn_master)

        btn_slave = QPushButton("Réguler Slave")
        btn_slave.clicked.connect(lambda: self.run_regulation(self.srfd_amp_slave, "MEASurement2:RESult:ACTual?"))
        layout.addWidget(btn_slave)

        btn_next = QPushButton("Suivant")
        btn_next.setStyleSheet(f"background-color:{GE_PURPLE}; color:white; padding:10px; border-radius:8px;")
        btn_next.clicked.connect(next_callback)
        layout.addWidget(btn_next)

        self.setLayout(layout)

    def init_instruments(self):
        self.result_display.append("✅ Instruments initialisés et ampli en standby (simulation).\n")

    def run_regulation(self, srfd_amp, meas_cmd):
        TARGET_DB = 69
        TOLERANCE = 0.2

        current_gain = 1000
        self.result_display.append(f"Départ DAC={current_gain} (simulation)")

        error_code = "00"
        decoded = "Aucun défaut détecté (simulation)"

        msg = []
        msg.append(f"Erreur brute (0x3014) : {error_code}")
        msg.append(f"Erreur décodée : {decoded}")

        self.result_display.append("\n".join(msg))
        QApplication.processEvents()

        simulated_steps = [
            (current_gain, 67.5),
            (current_gain + 5, 68.5),
            (current_gain + 8, 69.1),
        ]

        for dac, db_value in simulated_steps:
            self.result_display.append(f"DAC={dac}, Mesuré={db_value:.2f} dB (simulation)")
            QApplication.processEvents()
            time.sleep(0.1)

        final_db = simulated_steps[-1][1]
        self.result_display.append(f"✅ Objectif atteint: {final_db:.2f} dB (simulation)\n")

        self.result_display.append("ℹ️ Régulation terminée, ampli en standby et générateurs OFF (simulation).\n")

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SRFD_Regulation_{ts}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Logo
        story.append(Image(os.path.join(BASE_DIR, "Pics", "GE_Logo.png"), width=80, height=80))
        story.append(Spacer(1, 20))


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


        # Résultats régulation
        story.append(Paragraph("<b>Résultats Régulation</b>", styles["Heading2"]))
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

        network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

        try:
            shutil.copy(csv_file, network_path)
            self.result_display.append("📤 CSV envoyé sur EDHR.")
        except Exception as e:
            self.result_display.append(f"❌ Erreur envoi EDHR : {e}")


        self.result_display.append(f"Export CSV effectué : {csv_file}")
