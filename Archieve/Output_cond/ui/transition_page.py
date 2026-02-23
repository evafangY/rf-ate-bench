from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from Output_cond.ui.colors import GE_PURPLE
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TransitionPage(QWidget):
    def __init__(self, message, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel(message)
        label.setFont(QFont("Arial", 32 if first else 26, QFont.Bold))
        label.setStyleSheet(f"color: {GE_PURPLE};")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        if image_path:
            pixmap = QPixmap(os.path.join(BASE_DIR, "Pics", image_path))
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            if not pixmap.isNull():
                img_label.setPixmap(pixmap.scaled(QSize(1900, 600), Qt.KeepAspectRatio))
            else:
                img_label.setText("Image manquante")
            layout.addWidget(img_label)

        btn = QPushButton("Suivant")
        btn.setFont(QFont("Arial", 12, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GE_PURPLE};
                color: white;
                padding: 12px 30px;
                border-radius: 10px;
            }}
        """)
        btn.clicked.connect(next_callback)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
