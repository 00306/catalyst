from PyQt5.QtWidgets import QMessageBox, QWidget, QStackedWidget, QVBoxLayout
from src.service.project_service import ProjectService
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from .project_view import ProjectView
from src.model.gpc_data_set import GPCDataset, Signal
from src.core.theme.tokens import UI_TAG

class Workspace(QWidget):
    sig_project_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("class", UI_TAG.BG_BASE)

        self.current_file_path = None
        self.view_cache = {}
        self.cache_order = []
        self.MAX_CACHE = 7

        self.view_stack = QStackedWidget()

        self._pending_file_path = None
        self._load_timer = QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.setInterval(200)
        self._load_timer.timeout.connect(self._execute_load_project)

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 20, 0, 20)
        self.main_layout.setSpacing(0)

        self.main_layout.addWidget(self.view_stack)


    def load_project(self, file_path: str):
        self._pending_file_path = file_path
        self._load_timer.start()


        self.current_file_path = file_path

    def _execute_load_project(self):
        if not self._pending_file_path:
            return

        file_path = self._pending_file_path
        self.current_file_path = file_path


        try:
            metadata, data_dict = ProjectService.load_project_data(file_path)
            
            if file_path in self.view_cache:
                self._handle_cache_hit(file_path)
                return
            
            target_det = metadata.default_detector

            X = data_dict['x']
            Y = data_dict['y']
            if target_det in data_dict:
                Z = data_dict[target_det]
            else:
                remaining_keys = [k for k in data_dict.keys() if k not in ['x', 'y']]
                Z = data_dict[remaining_keys[0]]

            
                
            self._handle_cache_miss(file_path, metadata, X, Y, Z)

        except Exception as e:
            QMessageBox.critical(self, "프로젝트 로드 실패", f"데이터를 불러오는 중 오류 발생: {str(e)}")

    def handle_metadata_update(self, updated_meta: dict):
        if not self.current_file_path:
            return
            
        ProjectService.update_metadata_in_zip(self.current_file_path, updated_meta)
        self.sig_project_updated.emit()

    def _handle_cache_hit(self, file_path: str):
        target_view = self.view_cache[file_path]
        self.view_stack.setCurrentWidget(target_view)
 
        self.cache_order.remove(file_path)
        self.cache_order.append(file_path)


    
    def _handle_cache_miss(self, folder_path: str, metadata, X, Y, Z):
        dataset = GPCDataset(folder_path, metadata=metadata)

        det_name = metadata.default_detector
        signal_list = []
        for i, s_name in enumerate(metadata.sample_names):

            method = metadata.methods.get(s_name, "Unknown")
            date = metadata.analysis_dates.get(s_name, "Unknown")
            inst = metadata.instruments.get(s_name, "Unknown Device")

            sig = Signal(
                sample_name=s_name,
                detector_name=det_name,
                time=X[i],
                intensity=Z[i],
                unit=metadata.z_unit_dict.get(det_name, ""),
                method=method,
                date=date,
                instrument=inst
            )
            signal_list.append(sig)
        
        dataset.signals[det_name] = signal_list
        
        new_view = ProjectView(dataset)
        new_view.sig_metadata_changed.connect(self.handle_metadata_update)

        new_view.update_data(X, Y, Z)

        self.view_stack.addWidget(new_view)
        self.view_stack.setCurrentWidget(new_view)

        self._manage_cache(folder_path, new_view)


    def _manage_cache(self, file_path: str, new_widget):
        self.view_cache[file_path] = new_widget
        self.cache_order.append(file_path)

        if len(self.cache_order) > self.MAX_CACHE:
            oldest_path = self.cache_order.pop(0)
            old_widget = self.view_cache.pop(oldest_path)
            
            self.view_stack.removeWidget(old_widget)
            old_widget.deleteLater()

        
