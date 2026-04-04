from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QWidget, QApplication
from src.ui.view.left_panel import LeftPanel
from PyQt5.QtCore import Qt
from src.ui.view.project_setup import ProjectSetupView
from src.ui.view.workspace import Workspace
from src.service.project_generator import ProjectGenerator
from PyQt5.QtWidgets import QDesktopWidget
from src.config.app_config import AppConfig
from src.core.theme.tokens import UI_TAG
from src.core.theme.theme_manager import ThemeManager
from PyQt5.QtGui import QFont, QIcon
from src.util.resource_path import resource_path


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        AppConfig.initialize()
        self.setWindowIcon(QIcon(resource_path("asset/app_icon/catalyst_icon.png")))
        self.setMinimumSize(1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setProperty("class", UI_TAG.BG_BASE)

        self.central_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.central_widget.setProperty("class", UI_TAG.BG_BASE)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        

        self.left_panel = LeftPanel()
        self.right_stack = QStackedWidget()
        self.right_stack.setAttribute(Qt.WA_StyledBackground, True)
        self.right_stack.setProperty("class", UI_TAG.BG_BASE)

        self.setup_page = ProjectSetupView()
        self.workspace_page = Workspace()

        screen_height = QDesktopWidget().availableGeometry().height()
        self.left_panel.setMaximumHeight(screen_height)
        self.right_stack.setMaximumHeight(screen_height)

        self.apply_theme()

        self.right_stack.addWidget(self.setup_page)
        self.right_stack.addWidget(self.workspace_page)

        self.main_layout.addWidget(self.left_panel, 2)
        self.main_layout.addWidget(self.right_stack, 8)

        self.left_panel.sig_new_project_clicked.connect(self.display_setup_page)
        self.left_panel.sig_project_selected.connect(self.handle_project_selected)
        self.left_panel.sig_theme_changed.connect(self.handle_theme_changed)
        self.setup_page.sig_setup_complete.connect(self.on_project_setup_complete)
        self.workspace_page.sig_project_updated.connect(self.left_panel.refresh_project_list)
        self.theme_manager.theme_changed.connect(self.apply_theme, Qt.QueuedConnection)

        
        self.showMaximized()

    def apply_theme(self):
        qss = self.theme_manager.get_resolved_theme()
        font_family = qss.get("font_family_main", "Arial")

        app_font = QFont(font_family)
        app_font.setHintingPreference(QFont.PreferNoHinting)
        QApplication.instance().setFont(app_font)

        qss_string = self.theme_manager.get_qss()
        QApplication.instance().setStyleSheet(qss_string)
    


    def display_setup_page(self):
        self.right_stack.setCurrentWidget(self.setup_page)

    def on_project_setup_complete(self, setup_data):
        self.builder = ProjectGenerator(setup_data)

        try:
            result = self.builder.run() 
            self.on_build_success(result) 
            
        except Exception as e:
            self.on_build_error(str(e))


    def on_build_success(self, saved_file_path: str):

        self.workspace_page.load_project(saved_file_path)
        self.right_stack.setCurrentWidget(self.workspace_page)
        self.left_panel.refresh_project_list()

    def on_build_error(self, error_msg: str):
        QMessageBox.critical(self, "프로젝트 생성 실패", error_msg)

    def handle_project_selected(self, file_path: str):
        self.right_stack.setCurrentWidget(self.workspace_page)
        self.workspace_page.load_project(file_path)

    def handle_theme_changed(self, new_mode):
        self.theme_manager.current_mode = new_mode
        self.theme_manager.theme_changed.emit(new_mode)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



        
    