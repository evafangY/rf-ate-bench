from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QSize
import os

GE_PURPLE = "#4B0082"
GE_LIGHT_PURPLE = "#F5F0FA"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Step(QWidget):
    def __init__(self, titre, image_path, next_callback, back_callback=None, security=False, first_step=False):
        super().__init__()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(GE_LIGHT_PURPLE))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        top_layout = QHBoxLayout()
        title = QLabel(titre)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {GE_PURPLE};")
        title.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo_pix = QPixmap("Pics/GE_Logo.png")
        if not logo_pix.isNull():
            logo.setPixmap(logo_pix.scaled(80, 80, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignRight | Qt.AlignTop)

        top_layout.addWidget(title, stretch=1)
        top_layout.addWidget(logo, stretch=0)
        layout.addLayout(top_layout)

        pixmap = QPixmap(os.path.join(BASE_DIR, "Pics", image_path))

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaled(QSize(1900, 610), Qt.KeepAspectRatio))
        else:
            img_label.setText("Image manquante")
        layout.addWidget(img_label)

        btn_layout = QHBoxLayout()
        self.done = False
        self.defaut = False

        # --- BOUTON RETOUR ---
        if back_callback and not first_step:
            back_btn = QPushButton("Retour")
            back_btn.setFont(QFont("Arial", 12, QFont.Bold))
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: gray;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 8px;
                }
            """)
            back_btn.clicked.connect(back_callback)
            btn_layout.addWidget(back_btn)

        # --- BOUTON DEFAUT ---
        defaut_btn = QPushButton("Défaut")
        defaut_btn.setFont(QFont("Arial", 12, QFont.Bold))
        defaut_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
            }
        """)
        defaut_btn.clicked.connect(self.mark_defaut)
        btn_layout.addWidget(defaut_btn)

        # --- BOUTON FAIT ---
        fait_btn = QPushButton("Fait")
        fait_btn.setFont(QFont("Arial", 12, QFont.Bold))
        fait_btn.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
            }
        """)
        fait_btn.clicked.connect(self.mark_done)
        btn_layout.addWidget(fait_btn)

        # --- BOUTON VALIDER ---
        if security:
            self.checkbox = QCheckBox("J'ai pris connaissance de l'information")
            self.checkbox.setStyleSheet(f"color: {GE_PURPLE}; font-weight: bold;")
            layout.addWidget(self.checkbox)

            self.validate_btn = QPushButton("Valider")
            self.validate_btn.setFont(QFont("Arial", 12, QFont.Bold))
            self.validate_btn.setEnabled(False)
            self.validate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8A6BBE;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 8px;
                }
            """)

            self.validate_btn.clicked.connect(lambda: self.try_next(next_callback))
            btn_layout.addWidget(self.validate_btn)

            self.checkbox.stateChanged.connect(self.update_validate_button_state)

        else:
            self.validate_btn = QPushButton("Valider")
            self.validate_btn.setFont(QFont("Arial", 12, QFont.Bold))
            self.validate_btn.setEnabled(False)
            self.validate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8A6BBE;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 8px;
                }
            """)
            self.validate_btn.clicked.connect(lambda: self.try_next(next_callback))
            btn_layout.addWidget(self.validate_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_validate_button_state(self):
        if hasattr(self, "checkbox"):
            can_validate = self.done and self.checkbox.isChecked() and not self.defaut
        else:
            can_validate = self.done and not self.defaut

        if can_validate:
            self.validate_btn.setEnabled(True)
            self.validate_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GE_PURPLE};
                    color: white;
                    padding: 8px 20px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: #5C1AA3;
                }}
            """)
        else:
            self.validate_btn.setEnabled(False)
            self.validate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8A6BBE;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 8px;
                }
            """)

    def mark_defaut(self):
        self.defaut = True
        self.done = False
        QMessageBox.warning(self, "Étape en défaut", "⚠️ Cette étape est en défaut.")
        self.update_validate_button_state()

    def mark_done(self):
        self.done = True
        self.defaut = False
        self.update_validate_button_state()

    def try_next(self, next_callback):
        if self.done and not self.defaut:
            next_callback()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Validation requise")
            if self.defaut:
                msg.setText("⚠️ Étape en défaut.\nImpossible de valider tant que ce n'est pas corrigé.")
            else:
                msg.setText("⚠️ Vous devez cliquer sur 'Fait' avant de valider.")
            msg.exec_()
