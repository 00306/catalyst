import os
from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QHBoxLayout, QHeaderView, QTableWidget, QStackedWidget, QStackedLayout, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout, QListView, QAbstractItemView
from .drop_zone_widget import DropZoneWidget
from src.core.theme.tokens import UI_TAG
from src.core.parser.agilent_parser import AgilentParser
import datetime


class ListHeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("class", UI_TAG.BG_HEADER)

    def init_ui(self):
        self.setFixedHeight(40)
    
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignVCenter)

        lbl_detector = QLabel("Detector")
        lbl_detector.setProperty("class", UI_TAG.TEXT_PANEL_HEADER)
        lbl_detector.setFixedWidth(90)
        lbl_detector.setAlignment(Qt.AlignCenter)

        lbl_name = QLabel("Folder")
        lbl_name.setProperty("class", UI_TAG.TEXT_PANEL_HEADER)
        lbl_name.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        lbl_size = QLabel("Size")
        lbl_size.setProperty("class", UI_TAG.TEXT_PANEL_HEADER)
        lbl_size.setFixedWidth(100)
        lbl_size.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        lbl_date = QLabel("Date")
        lbl_date.setProperty("class", UI_TAG.TEXT_PANEL_HEADER)
        lbl_date.setFixedWidth(130)
        lbl_date.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        spacer_action = QWidget()
        spacer_action.setFixedWidth(50)

        def get_separator():
            sep = QFrame()
            sep.setFixedWidth(1)
            sep.setProperty("class", UI_TAG.BORDER_BASE)
            return sep

        layout.addWidget(lbl_detector)
        layout.addWidget(get_separator())
        layout.addWidget(lbl_name, 1)
        layout.addWidget(get_separator())
        layout.addWidget(lbl_size)
        layout.addWidget(get_separator())
        layout.addWidget(lbl_date)
        layout.addWidget(get_separator())
        layout.addWidget(spacer_action)


class FolderSlotWidget(QWidget):
    sig_remove_requested = pyqtSignal(str)

    def __init__(self, detector, folder_name, folder_size, date, file_path):
        super().__init__()

        self.detector = detector
        self.folder_name = folder_name
        self.folder_size = folder_size
        self.date = date
        self.file_path = file_path
        
        self.init_ui()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("class", UI_TAG.BG_ITEM)

    def init_ui(self):
        self.setFixedHeight(55)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 0)
        main_layout.setSpacing(12)

        self.detector_lbl = QLabel(self.detector)
        self.detector_lbl.setFixedWidth(90)
        self.detector_lbl.setAlignment(Qt.AlignCenter)
        self.detector_lbl.setProperty("class", UI_TAG.TEXT_ITEM_TITLE)

        info_container = QVBoxLayout()
        info_container.setSpacing(0)    
        info_container.setContentsMargins(0, 0, 0, 0) 
        info_container.setAlignment(Qt.AlignVCenter)
        

        self.folder_name_lbl = QLabel(self.folder_name)
        self.folder_name_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.folder_name_lbl.setProperty("class", UI_TAG.TEXT_ITEM_TITLE)
        self.folder_name_lbl.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        self.path_lbl = QLabel(self.file_path)
        self.path_lbl.setMinimumWidth(300)
        self.path_lbl.setProperty("class", UI_TAG.TEXT_ITEM_SUBTITLE)
        self.path_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        info_container.addWidget(self.folder_name_lbl)
        info_container.addWidget(self.path_lbl)

        self.size_lbl = QLabel(self.folder_size)
        self.size_lbl.setFixedWidth(100)
        self.size_lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.size_lbl.setProperty("class", UI_TAG.TEXT_ITEM_TITLE)

        self.date_lbl = QLabel(self.date)
        self.date_lbl.setFixedWidth(130)
        self.date_lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.date_lbl.setProperty("class", UI_TAG.TEXT_ITEM_TITLE)

        self.btn_container = QWidget()
        self.btn_container.setFixedWidth(50)
        btn_layout = QHBoxLayout(self.btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedSize(28, 28)
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setProperty("class", UI_TAG.BTN_DANGER)

        self.remove_btn.clicked.connect(lambda: self.sig_remove_requested.emit(self.file_path))
        btn_layout.addWidget(self.remove_btn, 0, Qt.AlignCenter)

        def get_separator():
            sep = QFrame()
            sep.setFixedWidth(1)
            sep.setProperty("class", UI_TAG.BORDER_BASE)
            return sep

        main_layout.addWidget(self.detector_lbl)
        main_layout.addWidget(get_separator())
        main_layout.addLayout(info_container, 1)
        main_layout.addWidget(get_separator())
        main_layout.addWidget(self.size_lbl)
        main_layout.addWidget(get_separator())
        main_layout.addWidget(self.date_lbl)
        main_layout.addWidget(get_separator())
        main_layout.addWidget(self.btn_container)

class FileImportWidget(QWidget):
    sig_files_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setProperty("class", UI_TAG.BG_BASE)
        self.init_ui()
        

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 15, 0, 0)
        self.main_layout.setSpacing(15)
        

        self.drop_zone = DropZoneWidget()
        self.drop_zone.setFixedHeight(120)
        self.drop_zone.sig_files_received.connect(self._handle_files_received)
        self.main_layout.addWidget(self.drop_zone)

        error_vbox = QVBoxLayout()
        error_vbox.setSpacing(2)
        error_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_file_error = QLabel("Please add at least one folder")
        self.lbl_file_error.setProperty("class", UI_TAG.TEXT_DANGER)
        self.lbl_file_error.hide()
        
        error_vbox.addWidget(self.drop_zone)
        error_vbox.addWidget(self.lbl_file_error)

        self.main_layout.addLayout(error_vbox)

        self.list_section_layout = QVBoxLayout()
        self.list_section_layout.setSpacing(0)

        self.header = ListHeaderWidget()
        self.list_section_layout.addWidget(self.header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("transparent_scroll_area")
        self.scroll_area.viewport().setObjectName("transparent_viewport")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setFixedHeight(220)
        
        self.list_container = QWidget()
        
        self.list_container.setObjectName("transparent_content_widget")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()
        self.list_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.list_container)
        self.list_section_layout.addWidget(self.scroll_area)
        self.main_layout.addLayout(self.list_section_layout, 1)

        self.main_layout.addStretch()

    def _handle_files_received(self, paths):
        self.lbl_file_error.hide()
        self.drop_zone.clear_error_state()

        for path in paths:
            if path in self.get_selected_folders():
                continue

            try:
                detectors = AgilentParser.get_detector_names(path)
                main_detector = detectors[0] if detectors else "N/A"
                
                folder_name = os.path.basename(path.rstrip('/\\'))

                mtime = os.path.getmtime(path)
                date_obj = datetime.datetime.fromtimestamp(mtime)
                date_str = date_obj.strftime("%B %d, %Y")
                folder_size = self.get_folder_size(path)

                slot = FolderSlotWidget(
                    detector=main_detector,
                    folder_name=folder_name,
                    folder_size=folder_size,
                    date=date_str,
                    file_path=path
                )
                
                slot.sig_remove_requested.connect(self._handle_file_remove)
                
                self.list_layout.insertWidget(0, slot)

            except Exception as e:
                print(f"🚨 파일 로드 중 오류 발생 ({path}): {e}")

        self.sig_files_changed.emit(self.get_selected_folders())

    def apply_theme(self, current_theme):
        self.drop_zone.apply_theme(current_theme)

    def show_file_error(self, message):
        self.lbl_file_error.setText(message)
        self.lbl_file_error.show()
        self.drop_zone.set_error_state()

    def reset_form(self):
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget:
                self.list_layout.removeWidget(widget)
                widget.deleteLater()
                
        self.lbl_file_error.hide()
        if hasattr(self.drop_zone, 'clear_error_state'):
            self.drop_zone.clear_error_state()
            
        self.sig_files_changed.emit([])


    def get_folder_size(self, folder_path):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total_size < 1024:
                    return f"{total_size:.1f} {unit}"
                total_size /= 1024
        except Exception:
            return "Unknown"

    def _handle_file_remove(self, file_path):
        for i in range(self.list_layout.count()):
            widget = self.list_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'file_path') and widget.file_path == file_path:
                self.list_layout.removeWidget(widget)
                widget.deleteLater()
                break

        self.sig_files_changed.emit(self.get_selected_folders())

    def set_mode(self, mode):
        self.current_mode = mode
        
        if mode == "Multi-Detector":
            self.drop_zone.main_text.setText("Add 2 folders for Multi-Detector")
            self.drop_zone.sub_text.setText("Exactly 2 folders required")
        else:
            self.drop_zone.main_text.setText("Drag & Drop files here")
            self.drop_zone.sub_text.setText("Supports .csv, .txt, .raw files")

    def get_selected_folders(self, mode=None):
        folders = []
        for i in range(self.list_layout.count()):
            widget = self.list_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'file_path'):
                folders.append(widget.file_path)
        return folders