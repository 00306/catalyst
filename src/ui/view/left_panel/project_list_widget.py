from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import QSize
from .project_card_widget import ProjectCardWidget

class ProjectListWidget(QListWidget):
    def __init__(self):
        super().__init__()

    def minimumSizeHint(self):
        return QSize(0, 0)

    def add_project_card(self, title, date, desc):
        item = QListWidgetItem(self)
        card = ProjectCardWidget(title, date, desc)

        item.setSizeHint(card.sizeHint())

        self.addItem(item)
        self.setItemWidget(item, card)