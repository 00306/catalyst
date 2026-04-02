from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal


class PlotInteractionBridge(QObject):
    clicked_signal = pyqtSignal(str)
    slice_changed_signal = pyqtSignal(float, float)
    render_finished_signal = pyqtSignal()

    @pyqtSlot(str)
    def receive_sample_name(self, name):
        self.clicked_signal.emit(name)

    @pyqtSlot(float, float)
    def receive_slice_range(self, start_time, end_time):
        self.slice_changed_signal.emit(start_time, end_time)

    @pyqtSlot()
    def notify_render_finished(self):
        self.render_finished_signal.emit()


