from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import QDate
from datetime import datetime

class LoginPage(QWidget):
    def __init__(self, next_callback):
        super().__init__()
        layout = QVBoxLayout()

        # Champs texte classiques
        self.sso_field = QLineEdit(); self.sso_field.setPlaceholderText("Operator ID (SSO)")
        self.nom_field = QLineEdit(); self.nom_field.setPlaceholderText("Nom")
        self.prenom_field = QLineEdit(); self.prenom_field.setPlaceholderText("Prénom")
        self.serial_field = QLineEdit(); self.serial_field.setPlaceholderText("DUT Serial Number")

        # 🔵 Atelier → QComboBox
        self.atelier_field = QComboBox()
        self.atelier_field.addItems([
            "Atelier 1",
            "Atelier 2",
            "Atelier 3",
            "Atelier 4",
            "Atelier 5"
        ])
        self.atelier_field.setEditable(False)

        # 🔵 PN → QComboBox (tu modifieras les valeurs plus tard)
        self.pn_field = QComboBox()
        self.pn_field.addItems([
            "PN-001",
            "PN-002",
            "PN-003",
            "PN-004",
            "PN-005"
        ])
        self.pn_field.setEditable(False)

        # 🔵 PN Revision → texte (tu n’as rien demandé ici)
        self.pn_rev_field = QLineEdit()
        self.pn_rev_field.setPlaceholderText("PN Revision")

        # 🔵 Test Date → auto-remplie avec la date du jour
        self.test_date_field = QLineEdit()
        today = datetime.now().strftime("%Y-%m-%d")
        self.test_date_field.setText(today)

        # 🔵 Station ID → QComboBox
        self.station_field = QComboBox()
        self.station_field.addItems([
            "Station 1",
            "Station 2",
            "Station 3",
            "Station 4",
            "Station 5"
        ])
        self.station_field.setEditable(False)

        # Ajout dans le layout
        for w in [
            self.sso_field, self.nom_field, self.prenom_field,
            self.atelier_field, self.serial_field,
            self.pn_field, self.pn_rev_field,
            self.test_date_field, self.station_field
        ]:
            layout.addWidget(w)

        # Bouton valider
        btn = QPushButton("Valider")
        btn.clicked.connect(lambda: self.save_and_next(next_callback))
        layout.addWidget(btn)

        self.setLayout(layout)

    def save_and_next(self, next_callback):
        self.parent().parent().user_info = {
            "SSO": self.sso_field.text(),
            "Nom": self.nom_field.text(),
            "Prenom": self.prenom_field.text(),
            "Atelier": self.atelier_field.currentText(),  
            "DUT_Serial": self.serial_field.text(),
            "Part_Number": self.pn_field.currentText(),       
            "PN_Revision": self.pn_rev_field.text(),
            "Test_Date": self.test_date_field.text(),
            "Station_ID": self.station_field.currentText()     
        }
        next_callback()
