from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Output_cond.ui.colors import GE_PURPLE
import datetime

class MeasureBodyPage(QWidget):
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
        self.loading_label.setStyleSheet("background-color:#4B0082; color:white; font-weight:bold; padding:6px; border-radius:8px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        # Bouton lancer mesure
        btn_measure = QPushButton("Lancer mesure BODY")
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
        self.loading_label.show()
        QApplication.processEvents()

        results = {
            "J4": 1.23,
            "J6": -40.0,
            "J8": -38.0,
            "J10": -42.0,
        }

        text = "Mesures BODY:\n" + "\n".join([f"{k}: {v}" for k, v in results.items()])
        self.result_display.setText(text)
        self.parent().parent().body_results = results
        self.done = True
        self.loading_label.hide()
