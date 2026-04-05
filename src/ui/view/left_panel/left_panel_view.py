from PyQt5.QtWidgets import QLabel, QListWidgetItem, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QAbstractItemView, QDialog, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt
from .project_list_widget import ProjectListWidget
from src.service.project_service import ProjectService
from .project_card_widget import ProjectCardWidget
from src.core.theme.tokens import UI_TAG
from pathlib import Path
from src.ui.view.dialog import ConfirmDialog
from src.core.theme.icons import SVG_ICONS
from src.ui.component.segment_control import SegmentControl
from src.core.theme.theme_manager import ThemeManager

class LeftPanel(QWidget):
        sig_project_selected = pyqtSignal(str)
        sig_new_project_clicked = pyqtSignal()
        sig_theme_changed = pyqtSignal(str)

        def __init__(self):
                super().__init__()
                self.theme_manager = ThemeManager()
                self.init_ui()
                
                self.setProperty("class", UI_TAG.BG_BASE)
                self.setAttribute(Qt.WA_StyledBackground, True)

        def init_ui(self):
                self.main_layout = QVBoxLayout(self)
                self.main_layout.setContentsMargins(15, 20, 15, 20)
                self.main_layout.setSpacing(10)

                self.set_up_theme_selector()
                self.setup_new_project_button()
                self.setup_project_list()
                

        def setup_new_project_button(self):
                header_container = QWidget()
                header_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                header_layout = QHBoxLayout(header_container)
                header_layout.setContentsMargins(12, 10, 12, 0)
                header_layout.setSpacing(0)
                
                self.projects_label = QLabel("PROJECTS")
                self.projects_label.setProperty("class", UI_TAG.TEXT_VIEW_TITLE)

                self.add_btn = QPushButton("+")
                self.add_btn.setFixedSize(24, 24)
                self.add_btn.setCursor(Qt.PointingHandCursor)
                self.add_btn.setProperty("class", UI_TAG.BTN_PANEL_ADD)
                self.add_btn.clicked.connect(self.sig_new_project_clicked.emit)

                
                header_layout.addWidget(self.projects_label)
                header_layout.addStretch()
                header_layout.addWidget(self.add_btn)

                self.main_layout.addWidget(header_container)
        
        def setup_project_list(self):
                list_container = QWidget()
                
                list_layout = QVBoxLayout(list_container)
                list_layout.setContentsMargins(0, 0, 0, 0)
                list_layout.setSpacing(0)

                self.project_list = ProjectListWidget()
                self.project_list.setSpacing(6)
                self.project_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
                self.project_list.verticalScrollBar().setSingleStep(15)
                self.project_list.setProperty("class", UI_TAG.BG_PANEL)
                self.project_list.setMinimumHeight(0) 
    
                self.project_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
                
                
                self.project_list.currentItemChanged.connect(self.on_current_item_changed)
                self.project_list.itemClicked.connect(self.on_item_clicked)
                self.refresh_project_list()
                self.project_list.clearSelection()
                self.project_list.clearFocus()
                
                list_layout.addWidget(self.project_list)
                self.main_layout.addWidget(list_container, 1)

        def set_up_theme_selector(self):
                svg_text_moon = SVG_ICONS["moon"]
                svg_text_paper = SVG_ICONS["paper"]

                theme_options = [
                        ("dark", svg_text_moon),
                        ("paper", svg_text_paper)
                ]

                self.theme_selector = SegmentControl(items=theme_options, default_value=self.theme_manager.current_mode)
                self.theme_selector.selectionChanged.connect(self.on_theme_changed)

                bottom_container = QWidget()
                bottom_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                bottom_layout = QHBoxLayout(bottom_container)
                bottom_layout.setContentsMargins(0, 0, 0, 0)
                bottom_layout.addWidget(self.theme_selector)
                bottom_layout.addStretch()
                
                self.theme_selector._refresh_icons(self.theme_manager.get_resolved_theme())

                self.main_layout.addWidget(bottom_container, 0)


        def on_theme_changed(self, new_mode):
                self.sig_theme_changed.emit(new_mode)
                self.theme_selector._refresh_icons(self.theme_manager.get_resolved_theme())


        def on_current_item_changed(self, current, previous):
                if previous:
                        prev_widget = self.project_list.itemWidget(previous)
                        if prev_widget:
                                prev_widget.set_selected(False)

                if current:
                        curr_widget = self.project_list.itemWidget(current)
                        if curr_widget:
                                curr_widget.set_selected(True)


        def refresh_project_list(self):
                self.project_list.clear()

                projects = ProjectService.get_recent_projects()

                for item_data in projects:
                        item = QListWidgetItem()
                        item.setData(Qt.UserRole, item_data.file_path)
                        meta = item_data.metadata

                        title = meta.project_name
                        project_type = meta.mode
                        default_detector = meta.default_detector

                        signals_count = str(len(meta.sample_names)) if meta.sample_names else "0"

                        card = ProjectCardWidget(
                                file_path=item_data.file_path,
                                title=title,
                                project_type=project_type,
                                date_str=item_data.date_str,
                                detector=default_detector,
                                signals=signals_count,
                                desc=meta.description
                        )
                        
                        item.setSizeHint(card.sizeHint())

                        card.sig_delete_requested.connect(self.handle_project_delete)
                        
                        self.project_list.addItem(item)
                        self.project_list.setItemWidget(item, card)

        def on_item_clicked(self, item):
                file_path = item.data(Qt.UserRole)

                if file_path:
                        self.sig_project_selected.emit(file_path)


        def handle_project_delete(self, file_path):
                target_name = Path(file_path).stem
                
                dialog = ConfirmDialog(
                    parent=self, 
                    title="Delete Project", 
                    message=f"Are you sure you want to delete\n'{target_name}'?"
                )

                if dialog.exec_() == QDialog.Accepted:
                        success = ProjectService.delete_project(file_path)
                        
                        if success:
                                self.refresh_project_list()




        