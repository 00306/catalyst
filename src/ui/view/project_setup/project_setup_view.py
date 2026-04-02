from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QComboBox, QLabel)
from .project_info_widget import ProjectInfoWidget
from .file_import_widget import FileImportWidget
from PyQt5.QtCore import pyqtSignal, Qt
from src.model.project_config import ProjectConfig
from src.config.app_config import AppConfig
from src.core.parser.agilent_parser import AgilentParser
from src.core.theme.tokens import UI_TAG
from src.core.theme.theme_manager import ThemeManager

class ProjectSetupView(QWidget):
    sig_setup_complete = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.init_ui()
        self.setProperty("class", UI_TAG.BG_BASE)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.file_import_seg.sig_files_changed.connect(self._handle_detector_scan)
        self.project_info_seg.sig_mode_change.connect(self.file_import_seg.set_mode)
        self.btn_create.clicked.connect(self.handle_create_project)

        self.on_theme_changed(self.theme_manager.current_mode)
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.has_detectors = False
    

        self.project_info_seg = ProjectInfoWidget()
        self.file_import_seg = FileImportWidget()

        self.main_layout.addWidget(self.project_info_seg)
        self.main_layout.addWidget(self.file_import_seg)

        self.setup_bottom_actions()


    def on_theme_changed(self, theme):
        current_theme = self.theme_manager.get_resolved_theme()
        self.file_import_seg.apply_theme(current_theme)

    def handle_create_project(self):
        mode = self.project_info_seg.get_mode()
        p_name = self.project_info_seg.get_project_name().strip()
        p_desc = self.project_info_seg.input_description.toPlainText()
        folder_paths = self.file_import_seg.get_selected_folders(mode)
        selected_detector = self.combo_detector.currentText()

        has_error = False

        if not p_name:
            self.project_info_seg.show_name_error()
            self.project_info_seg.input_project_name.setFocus()
            has_error = True
            
        if not folder_paths:
            self.file_import_seg.show_file_error(" Please add at least one folder")
            has_error = True
        elif mode == "Multi-Detector" and len(folder_paths) != 2:
            self.file_import_seg.show_file_error(" Multi-Detector mode requires exactly 2 folders.")
            has_error = True

        if has_error:
            return

        if mode == "Multi-Detector":
            ext = ".mdz"
        else:
            mode = "Overlay"
            ext = ".pkz"

        save_dir = AppConfig.PROJECT_DIR
        save_dir.mkdir(parents=True, exist_ok=True)
        
        save_path = save_dir / f"{p_name}{ext}"
        counter = 2
        while save_path.exists():
            save_path = save_dir / f"{p_name} ({counter}){ext}"
            counter += 1

        p_name = save_path.stem

        common_detectors = [self.combo_detector.itemText(i) 
                                for i in range(self.combo_detector.count())]

        setup_data = ProjectConfig(
            project_name=p_name, 
            description=p_desc, 
            mode=mode, 
            folder_paths=folder_paths, 
            target_detector=selected_detector,
            common_detectors=common_detectors,
            save_path=save_path
        )

        self.sig_setup_complete.emit(setup_data)
        self.reset_view()


    def reset_view(self):
        self.project_info_seg.reset_form()
        self.file_import_seg.reset_form()
        self.combo_detector.clear()

    def _handle_detector_scan(self, folder_paths):
        if not folder_paths:
            self.combo_detector.clear()
            self.has_detectors = False
            return

        detector_sets = []

        for path in folder_paths:
            det_list = AgilentParser.get_detector_names(path)
            detector_sets.append(set(det_list))

        common_detectors = set.intersection(*detector_sets) if detector_sets else set()
        
        self.combo_detector.clear()
        self.combo_detector.addItems(sorted(list(common_detectors)))
        


    def setup_bottom_actions(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 40)

        det_container = QVBoxLayout()
        lbl_title = QLabel("DETECTOR SELECT")
        lbl_title.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)
        
        self.combo_detector = QComboBox()
        self.combo_detector.setMinimumWidth(250)
        self.combo_detector.setFixedHeight(42)
        self.combo_detector.setProperty("class", UI_TAG.BG_INPUT)
        
        det_container.addWidget(lbl_title)
        det_container.addWidget(self.combo_detector)
        bottom_layout.addLayout(det_container)

        bottom_layout.addStretch()

        self.btn_create = QPushButton("Create Project")
        self.btn_create.setFixedSize(180, 48)
        self.btn_create.setCursor(Qt.PointingHandCursor)
        self.btn_create.setProperty("class", UI_TAG.BTN_PRIMARY)
        
        
        bottom_layout.addWidget(self.btn_create, alignment=Qt.AlignBottom)
        self.main_layout.addLayout(bottom_layout)