from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from Input_cond.ui.colors import GE_PURPLE

class TransitionPage(QWidget):
    def __init__(self, titre, next_callback, image_path=None, first=False):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel(titre)
        label.setFont(QFont("Arial", 32 if first else 26, QFont.Bold))
        label.setStyleSheet(f"color:{GE_PURPLE};")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        if image_path:
            pixmap = QPixmap("Pics/" + image_path)
            img = QLabel()
            img.setAlignment(Qt.AlignCenter)
            if not pixmap.isNull():
                img.setPixmap(pixmap.scaled(QSize(1900, 610), Qt.KeepAspectRatio))
            layout.addWidget(img)

        btn = QPushButton("Suivant")
        btn.setFont(QFont("Arial", 12, QFont.Bold))
        btn.setStyleSheet(f"background-color:{GE_PURPLE}; color:white; padding:12px; border-radius:10px;")
        btn.clicked.connect(next_callback)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
