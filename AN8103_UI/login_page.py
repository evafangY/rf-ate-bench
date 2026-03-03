from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import datetime


class LoginPage(QWidget):
    def __init__(self, start_callback):
        super().__init__()
        self.start_callback = start_callback

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("SRFD II RF Amplifier 1.5T ATE")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(title)

        self.operator_edit = QLineEdit()
        self.station_edit = QLineEdit()
        self.ate_combo = QComboBox()
        self.ate_combo.addItems(["ATE01", "ATE02"])
        self.dut_serial_edit = QLineEdit()
        self.part_number_edit = QLineEdit()
        self.date_edit = QLineEdit()

        self.station_edit.setText("01")
        self.part_number_edit.setText("2351573-02")
        self.date_edit.setText(datetime.datetime.now().strftime("%Y-%m-%d"))

        def add_row(label_text, widget):
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(150)
            row.addWidget(label)
            row.addWidget(widget)
            layout.addLayout(row)

        add_row("SSO de l'opérateur:", self.operator_edit)
        add_row("ID de la station:", self.station_edit)
        add_row("Sélection ATE:", self.ate_combo)
        add_row("Numéro de série du DUT:", self.dut_serial_edit)
        add_row("Numéro de pièce:", self.part_number_edit)
        add_row("Date:", self.date_edit)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        start_button = QPushButton("Démarrer la séquence de tests")
        start_button.setFont(QFont("Arial", 14, QFont.Bold))
        start_button.clicked.connect(self.on_start)
        layout.addWidget(start_button)

        self.setLayout(layout)

    def on_start(self):
        tech = {
            "SSO": self.operator_edit.text().strip(),
            "Station_ID": self.station_edit.text().strip(),
            "ATE_ID": self.ate_combo.currentText(),
        }
        dut = {
            "DUT_Serial": self.dut_serial_edit.text().strip(),
            "Part_Number": self.part_number_edit.text().strip(),
            "Test_Date": self.date_edit.text().strip(),
        }
        if not tech["SSO"]:
            self.status_label.setText("Veuillez entrer le SSO de l'opérateur.")
            return
        self.start_callback(tech, dut)
