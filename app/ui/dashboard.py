from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QProgressBar, QScrollArea, QListWidget
)
from PySide6.QtCore import Qt
from app.ui.workflow import WorkflowBar
from app.ui.widgets import ImagePanel, StatCard, SectionPanel
from app.ui.charts import LineChartCanvas, DonutChartCanvas
from app.utils import theme
from app.database.database import db
from app.models.model_manager import model_manager
from app.utils.animations import CountUpAnimator


class Dashboard(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(14)

        status_row = QHBoxLayout()
        self.status_cards = {}
        for key, label in [
            ("system_status", "SYSTEM STATUS"),
            ("model_status", "MODEL STATUS"),
            ("processing_mode", "PROCESSING"),
            ("dataset_status", "DATASET STATUS"),
        ]:
            card = StatCard(label, "--", theme.SUCCESS)
            status_row.addWidget(card)
            self.status_cards[key] = card
        outer.addLayout(status_row)

        stats_row = QHBoxLayout()
        self.summary_cards = {}
        for key, label, accent in [
            ("total_analyses", "TOTAL ANALYSES", theme.ACCENT_CYAN),
            ("changes_detected", "CHANGES DETECTED", theme.ACCENT_PURPLE),
            ("average_change", "AVERAGE CHANGE", theme.WARNING),
            ("model_performance", "MODEL PERFORMANCE", theme.ACCENT_PINK),
        ]:
            card = StatCard(label, "0", accent)
            stats_row.addWidget(card)
            self.summary_cards[key] = card
        outer.addLayout(stats_row)

        self.workflow = WorkflowBar()
        outer.addWidget(self.workflow)

        images_row = QHBoxLayout()
        self.before_panel = ImagePanel("BEFORE IMAGE", theme.SUCCESS)
        self.after_panel = ImagePanel("AFTER IMAGE", theme.ACCENT_CYAN)
        self.mask_panel = ImagePanel("PREDICTED CHANGE MASK", theme.ACCENT_PURPLE)
        self.overlay_panel = ImagePanel("OVERLAY (CHANGE HIGHLIGHTED)", theme.ACCENT_PINK)
        for p in [self.before_panel, self.after_panel, self.mask_panel, self.overlay_panel]:
            images_row.addWidget(p)
        outer.addLayout(images_row, stretch=3)

        metrics_row = QHBoxLayout()
        metrics_panel = SectionPanel("PERFORMANCE METRICS", theme.ACCENT_PURPLE)
        metrics_cards = QHBoxLayout()
        self.metric_cards = {}
        for key, label, accent in [
            ("iou", "IoU (Jaccard)", theme.ACCENT_PURPLE),
            ("dice", "Dice Coefficient", theme.ACCENT_CYAN),
            ("precision", "Precision", theme.ACCENT_BLUE if hasattr(theme, "ACCENT_BLUE") else theme.ACCENT_CYAN),
            ("recall", "Recall", theme.WARNING),
            ("f1_score", "F1-Score", theme.ACCENT_PINK),
            ("change_percent", "Change %", theme.ACCENT_CYAN),
        ]:
            card = StatCard(label, "--", accent)
            metrics_cards.addWidget(card)
            self.metric_cards[key] = card
        metrics_panel.body().addLayout(metrics_cards)
        metrics_row.addWidget(metrics_panel, stretch=3)

        donut_panel = SectionPanel("CHANGE DISTRIBUTION", theme.ACCENT_PINK)
        self.donut_chart = DonutChartCanvas()
        donut_panel.body().addWidget(self.donut_chart)
        self.donut_legend = QLabel("Changed: --%   Unchanged: --%")
        self.donut_legend.setStyleSheet(f"color:{theme.TEXT_SECONDARY};")
        donut_panel.body().addWidget(self.donut_legend)
        metrics_row.addWidget(donut_panel, stretch=1)
        outer.addLayout(metrics_row, stretch=2)

        bottom_row = QHBoxLayout()

        training_panel = SectionPanel("TRAINING PROGRESS", theme.ACCENT_CYAN)
        self.training_chart = LineChartCanvas(width=4.5, height=2.6)
        training_panel.body().addWidget(self.training_chart)
        bottom_row.addWidget(training_panel, stretch=2)

        model_panel = SectionPanel("MODEL INFORMATION", theme.ACCENT_PURPLE)
        self.model_info_label = QLabel("No model loaded.")
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:12px;")
        model_panel.body().addWidget(self.model_info_label)
        bottom_row.addWidget(model_panel, stretch=1)

        logs_panel = SectionPanel("SYSTEM LOGS", theme.ACCENT_CYAN)
        self.logs_list = QListWidget()
        self.logs_list.setStyleSheet(f"background-color:{theme.BG_PANEL}; border:none; color:{theme.TEXT_SECONDARY};")
        logs_panel.body().addWidget(self.logs_list)
        bottom_row.addWidget(logs_panel, stretch=1)

        outer.addLayout(bottom_row, stretch=3)

        footer = QFrame()
        footer.setObjectName("Panel")
        footer_layout = QHBoxLayout(footer)
        self.overall_progress = QProgressBar()
        self.overall_progress.setValue(0)
        footer_layout.addWidget(QLabel("OVERALL PROGRESS"))
        footer_layout.addWidget(self.overall_progress, stretch=2)

        self.run_btn = QPushButton("RUN ANALYSIS")
        self.run_btn.setObjectName("PrimaryButton")
        self.export_btn = QPushButton("EXPORT RESULTS")
        self.report_btn = QPushButton("GENERATE REPORT")
        self.report_btn.setObjectName("SuccessButton")
        footer_layout.addWidget(self.run_btn)
        footer_layout.addWidget(self.export_btn)
        footer_layout.addWidget(self.report_btn)
        outer.addWidget(footer)

        self.stats_row_container = None
        self.refresh()

    def append_log(self, message):
        self.logs_list.insertItem(0, message)
        while self.logs_list.count() > 30:
            self.logs_list.takeItem(self.logs_list.count() - 1)

    def refresh(self):
        stats = db.dashboard_stats()
        model = model_manager

        self.status_cards["system_status"].set_value("READY")
        self.status_cards["model_status"].set_value("LOADED" if model.model is not None else "NOT TRAINED")
        self.status_cards["processing_mode"].set_value("CPU")

        from app.dataset.dataset_manager import dataset_manager
        dataset_ready = dataset_manager.is_dataset_ready()
        self.status_cards["dataset_status"].set_value("READY" if dataset_ready else "NOT FOUND")

        self.summary_cards["total_analyses"].animator.animate_to(stats["total_analyses"], decimals=0)
        self.summary_cards["changes_detected"].animator.animate_to(stats["changes_detected"], decimals=0)
        self.summary_cards["average_change"].animator.animate_to(stats["average_change"], is_percent=True, decimals=2)

        if self.app_state.last_metrics:
            perf = self.app_state.last_metrics.get("dice") or self.app_state.last_metrics.get("f1_score")
            self.summary_cards["model_performance"].set_value(f"{perf:.2%}" if perf is not None else "--")
        else:
            self.summary_cards["model_performance"].set_value("--")

        if model.model is not None:
            info = model.summary_info() or {}
            lines = [
                f"Model Name : {info.get('model_name', 'Lightweight U-Net')}",
                f"Input Shape : {info.get('input_shape', '-')}",
                f"Total Parameters : {info.get('total_parameters', '-')}",
                f"Trainable Params : {info.get('trainable_parameters', '-')}",
                f"Optimizer : {info.get('optimizer', 'Adam')}",
                f"Loss Function : {info.get('loss', 'BCE + Dice')}",
                f"Epochs Trained : {info.get('epochs', '-')}",
                f"Batch Size : {info.get('batch_size', '-')}",
            ]
            self.model_info_label.setText("\n".join(lines))
        else:
            self.model_info_label.setText("MODEL STATUS: NOT TRAINED\n\nTrain a model or load an existing one from the Training or Model Information pages.")

        history = db.latest_training_history()
        if history:
            series = {}
            if "loss" in history:
                series["Training Loss"] = history["loss"]
            if "val_loss" in history:
                series["Validation Loss"] = history["val_loss"]
            self.training_chart.plot_series(series, xlabel="Epoch", ylabel="Loss")
        else:
            self.training_chart.plot_series({}, xlabel="Epoch", ylabel="Loss")

    def update_metrics(self, metrics_dict):
        for key, card in self.metric_cards.items():
            if key in metrics_dict:
                val = metrics_dict[key]
                if key == "change_percent":
                    card.set_value(f"{val:.2f}%")
                else:
                    card.set_value(f"{val:.4f}")
        change = metrics_dict.get("change_percent", 0.0)
        self.donut_chart.plot(change, 100 - change)
        self.donut_legend.setText(f"Changed: {change:.2f}%   Unchanged: {100 - change:.2f}%")

    def set_images(self, before, after, mask, overlay):
        self.before_panel.set_image(before)
        self.after_panel.set_image(after)
        self.mask_panel.set_image(mask)
        self.overlay_panel.set_image(overlay)
