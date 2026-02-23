from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize

GE_PURPLE = "#4B0082"

class TransitionPage(QWidget):
    def __init__(self, message, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel(message)
        label.setFont(QFont("Arial", 32 if first else 26, QFont.Bold))
        label.setStyleSheet(f"color:{GE_PURPLE};")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        if image_path:
            img = QLabel()
            pix = QPixmap("Pics/" + image_path)
            if not pix.isNull():
                img.setPixmap(pix.scaled(QSize(1900, 600), Qt.KeepAspectRatio))
            layout.addWidget(img)

        b = QPushButton("Suivant")
        b.clicked.connect(next_callback)
        layout.addWidget(b, alignment=Qt.AlignCenter)

        self.setLayout(layout)
