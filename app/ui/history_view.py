from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox
)
from app.database.database import db
from app.utils import theme


class HistoryView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("ANALYSIS HISTORY")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Change %", "Regions", "Confidence", "Time (s)", "Severity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("REFRESH")
        self.delete_btn = QPushButton("DELETE SELECTED")
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.delete_btn)
        layout.addLayout(btn_row)

        self.refresh_btn.clicked.connect(self.refresh)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.refresh()

    def refresh(self):
        rows = db.fetch_analyses()
        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            (aid, date, before_image, after_image, model_name, change_percent,
             num_regions, confidence, processing_time, severity) = row
            values = [aid, date, f"{change_percent:.2f}", num_regions, f"{confidence:.4f}", f"{processing_time:.2f}", severity]
            for c_idx, val in enumerate(values):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))

    def delete_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "HISTORY", "Select a row to delete first.")
            return
        row = selected[0].row()
        analysis_id = int(self.table.item(row, 0).text())
        db.delete_analysis(analysis_id)
        self.refresh()
