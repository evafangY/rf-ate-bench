from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Output_cond.core.export_utils import export_results
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from Output_cond.ui.colors import GE_PURPLE
import datetime
import shutil
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
            results = {
                "J3": 1.11,
                "J5": -35.0,
                "J7": -36.5,
                "J9": -37.0,
            }
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
            story.append(Image(os.path.join(BASE_DIR, "Pics", "GE_Logo.png"), width=80, height=80))

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
            #output_list = []
            #{if body:
             #   output_list += [f"BODY {k}: {v}" for k, v in body.items()]
            #output_list += [f"HEAD {k}: {v}" for k, v in results.items()]

            output_list = {}

            if body:
                for k, v in body.items():
                    output_list[f"BODY_{k}"] = v

            for k, v in results.items():
                output_list[f"HEAD_{k}"] = v

            # Export CSV
            csv_file = export_results(output_list, user, ts)


            network_path = r"\\10.21.138.117\ManualImport\ERC\XFDPS\RawFile"

            try:
                shutil.copy(csv_file, network_path)
                self.result_display.append("📤 CSV envoyé sur EDHR.")
            except Exception as e:
                self.result_display.append(f"❌ Erreur envoi EDHR : {e}")


            self.result_display.append(f"\n ✅Export CSV effectué : SRFD_Measures_{csv_file}")
            self.done = True

        except Exception as e:
            self.result_display.setText(f"❌ Erreur mesure HEAD:\n{str(e)}")
            self.defaut = True
        finally:
            self.loading_label.hide()
