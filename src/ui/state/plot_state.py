from PyQt5.QtCore import QObject, pyqtSignal

class PlotState(QObject):
    sig_changed = pyqtSignal()
    sig_analysis_range_changed = pyqtSignal(str, float, float)
    sig_cos_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.full_X, self.full_Y, self.full_Z = None, None, None
        self.curr_X, self.curr_Y, self.curr_Z = None, None, None

        self.view_mode = "line"
        
        self.cos_time_axis = None
        self.avg_Z = None
        self.cos_sync_Z = None
        self.cos_async_Z = None
        
        self.apply_to_all = True
        self.integration_ranges = {}
        self.current_sample_name = None


    def set_apply_to_all(self, state):
        self.apply_to_all = state

    def set_view_mode(self, mode):
        if self.view_mode == mode: return

        self.view_mode = mode
        self.sig_changed.emit()
    
    def load_initial_data(self, X, Y, Z, sample_names=None):

        self.full_X, self.full_Y, self.full_Z = X, Y, Z
        self.curr_X, self.curr_Y, self.curr_Z = X, Y, Z
        self.sample_name_list = sample_names or []
        self.sig_changed.emit()


    def update_cos_data(self, time_axis, avg_Z, sync_Z, async_Z):
        self.cos_time_axis = time_axis
        self.avg_Z = avg_Z
        self.cos_sync_Z = sync_Z
        self.cos_async_Z = async_Z

        self.sig_cos_updated.emit()

    def set_active_sample(self, sample_name: str):
        if self.current_sample_name == sample_name:
            self.current_sample_name = None
        else:
            self.current_sample_name = sample_name

    def update_analysis_range(self, start_t, end_t):
        if self.apply_to_all:
            for sample in self.sample_name_list:
                self.integration_ranges[sample] = (start_t, end_t)
            
            self.sig_analysis_range_changed.emit("ALL", start_t, end_t)
            return
            
        if self.current_sample_name:
            self.integration_ranges[self.current_sample_name] = (start_t, end_t)
            
            self.sig_analysis_range_changed.emit(self.current_sample_name, start_t, end_t)
