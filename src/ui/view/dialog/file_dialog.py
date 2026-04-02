from PyQt5.QtWidgets import QFileDialog, QListView, QTreeView, QAbstractItemView
from src.ui.component.file_dialog_proxy_style import FileDialogIconProxyStyle

class FileDialog(QFileDialog):
    def __init__(self, icon_color, parent=None, title="Select", default_dir="", filter_str="All Files (*.*)", mode="open_dir"):
        super().__init__(parent, title, default_dir, filter_str)
        
        
        self._modern_style = FileDialogIconProxyStyle(icon_color)
        self.setStyle(self._modern_style)

        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setViewMode(QFileDialog.Detail)

        if mode == "save":
            self.setAcceptMode(QFileDialog.AcceptSave)
        elif mode == "open_dir":
            self.setFileMode(QFileDialog.DirectoryOnly)
            self.setOption(QFileDialog.ShowDirsOnly, True)
        elif mode == "open_files":
            self.setFileMode(QFileDialog.ExistingFiles)

        if mode in ["open_dir", "open_files"]:
            file_view = self.findChild(QListView, 'listView')
            if file_view:
                file_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
            tree_view = self.findChild(QTreeView)
            if tree_view:
                tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)