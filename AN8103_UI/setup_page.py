from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


class SetupPage(QWidget):
    def __init__(self, proceed_callback):
        super().__init__()
        self.proceed_callback = proceed_callback
        self.target_index = -1
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        self.title_label = QLabel("Configuration Setup")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(self.title_label)
        
        self.instruction_label = QLabel("")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.instruction_label)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        confirm_btn = QPushButton("Configuration Prête / Continue")
        confirm_btn.setFont(QFont("Arial", 16, QFont.Bold))
        confirm_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        confirm_btn.clicked.connect(self.on_proceed)
        layout.addWidget(confirm_btn)
        
        self.setLayout(layout)

    def set_config(self, config_data, target_index):
        self.target_index = target_index
        title = config_data.get("title", "Setup Configuration")
        instruction = config_data.get("instruction", "")
        image_path = config_data.get("image", "")
        
        self.title_label.setText(title)
        self.instruction_label.setText(instruction)
        
        if image_path:
            pix = QPixmap(image_path)
            if not pix.isNull():
                self.image_label.setPixmap(pix.scaledToHeight(400, Qt.SmoothTransformation))
            else:
                self.image_label.clear()
        else:
            self.image_label.clear()

    def on_proceed(self):
        if self.target_index != -1:
            self.proceed_callback(self.target_index)
