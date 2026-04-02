from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import Qt
from src.core.theme.tokens import UI_TAG

class ConfirmDialog(QDialog):
    def __init__(self, parent=None, title="Confirm", message="Are you sure?"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 140) 

        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) 
        self.setAttribute(Qt.WA_TranslucentBackground)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QFrame(self)
        container.setProperty("class", UI_TAG.BG_ALERT)
        main_layout.addWidget(container)   

        layout = QVBoxLayout(container) 
        layout.setContentsMargins(20, 25, 20, 20)
        layout.setSpacing(15)

        # 받은 메시지를 화면에 출력
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setProperty("class", UI_TAG.TEXT_ALERT_BODY)
        layout.addWidget(msg_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", UI_TAG.BTN_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", UI_TAG.BTN_DANGER)
        delete_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)