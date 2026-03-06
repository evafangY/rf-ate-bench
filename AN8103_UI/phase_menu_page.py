from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .phase_config import PHASE_CONFIG


class PhaseMenuPage(QWidget):
    def __init__(self, phases, start_callback, eng_mode_callback, select_phase_callback, generate_pdf_callback, generate_csv_callback):
        super().__init__()
        self.select_phase_callback = select_phase_callback
        self.generate_pdf_callback = generate_pdf_callback
        self.generate_csv_callback = generate_csv_callback
        self.phase_buttons = []
        self.status_labels = []

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("Sélectionner le test")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Mode opérateur: les tests sont exécutés dans l'ordre.\nMode ingénieur: sélectionnez n'importe quel test.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 11))
        layout.addWidget(subtitle)

        for index, phase in enumerate(phases):
            row = QHBoxLayout()
            status = QLabel("Non testé")
            status.setFixedWidth(90)
            status.setAlignment(Qt.AlignCenter)
            status.setFont(QFont("Arial", 11))
            row.addWidget(status)

            cfg = PHASE_CONFIG.get(phase, {})
            display_name = cfg.get("display_name", phase)

            btn = QPushButton(f"{index + 1}. {display_name}")
            btn.setFont(QFont("Arial", 13))
            btn.setEnabled(False)

            def make_handler(i):
                def handler():
                    self.select_phase_callback(i)

                return handler

            btn.clicked.connect(make_handler(index))
            self.phase_buttons.append(btn)
            self.status_labels.append(status)
            row.addWidget(btn)
            layout.addLayout(row)

        button_row = QHBoxLayout()

        start_button = QPushButton("Démarrer la séquence (mode opérateur)")
        start_button.setFont(QFont("Arial", 14, QFont.Bold))
        start_button.clicked.connect(start_callback)
        button_row.addWidget(start_button)

        eng_button = QPushButton("Mode ingénieur")
        eng_button.setFont(QFont("Arial", 14, QFont.Bold))
        eng_button.clicked.connect(eng_mode_callback)
        button_row.addWidget(eng_button)

        pdf_button = QPushButton("Générer PDF")
        pdf_button.setFont(QFont("Arial", 14, QFont.Bold))
        pdf_button.clicked.connect(generate_pdf_callback)
        button_row.addWidget(pdf_button)

        csv_button = QPushButton("Générer CSV")
        csv_button.setFont(QFont("Arial", 14, QFont.Bold))
        csv_button.clicked.connect(generate_csv_callback)
        button_row.addWidget(csv_button)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def enable_engineering(self, enabled: bool):
        for btn in self.phase_buttons:
            btn.setEnabled(enabled)

    def set_phase_enabled(self, index: int, enabled: bool):
        if 0 <= index < len(self.phase_buttons):
            self.phase_buttons[index].setEnabled(enabled)

    def set_phase_status(self, index: int, ok: bool):
        if 0 <= index < len(self.status_labels):
            label = self.status_labels[index]
            if ok is None:
                label.setText("Non testé")
                label.setStyleSheet("color: black;")
                label.setFont(QFont("Arial", 11))
            elif ok:
                label.setText("Réussi")
                label.setStyleSheet("color: green;")
            else:
                label.setText("Échec")
                label.setStyleSheet("color: red;")
