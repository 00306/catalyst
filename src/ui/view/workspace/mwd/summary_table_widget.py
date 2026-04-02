from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem, QAbstractScrollArea, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt
from src.core.theme.theme_manager import ThemeManager
from src.core.theme.tokens import UI_TAG

class SummaryTableWidget(QWidget):
    sig_sample_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.results = []
        
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Sample", "Mn (Da)", "Mw (Da)", "PDI", "Range (min)"])

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setProperty("class", UI_TAG.BG_PANEL)

        self.table.setProperty("class", f"{UI_TAG.BG_PANEL} {UI_TAG.TEXT_PRIMARY}")

        self.table.cellClicked.connect(self._on_cell_clicked)

        self.main_layout.addWidget(self.table)

    def update_table(self, results_dict):
        self.table.setRowCount(len(results_dict))
        
        for row_idx, (sample_name, res) in enumerate(results_dict.items()):
            item_name = QTableWidgetItem(sample_name)
            item_mn = QTableWidgetItem(f"{res.mn:,.0f}")
            item_mw = QTableWidgetItem(f"{res.mw:,.0f}")
            item_pdi = QTableWidgetItem(f"{res.pdi:.2f}")
            item_range = QTableWidgetItem(f"{res.start_time:.1f} - {res.end_time:.1f}")

            for item in (item_mn, item_mw, item_pdi, item_range):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)


            self.table.setItem(row_idx, 0, item_name)
            self.table.setItem(row_idx, 1, item_mn)
            self.table.setItem(row_idx, 2, item_mw)
            self.table.setItem(row_idx, 3, item_pdi)
            self.table.setItem(row_idx, 4, item_range)

    def _on_cell_clicked(self, row, col):
        sample_name_item = self.table.item(row, 0)
        if sample_name_item:
            self.sig_sample_clicked.emit(sample_name_item.text())

