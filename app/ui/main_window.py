from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from app.ui.sidebar import Sidebar
from app.ui.header import Header
from app.ui.dashboard import Dashboard
from app.ui.upload_view import UploadView
from app.ui.preprocessing_view import PreprocessingView
from app.ui.prediction_view import PredictionView
from app.ui.results_view import ResultsView
from app.ui.visualization_view import VisualizationView
from app.ui.activation_maps_view import ActivationMapsView
from app.ui.metrics_view import MetricsView
from app.ui.training_view import TrainingView
from app.ui.dataset_view import DatasetView
from app.ui.model_view import ModelView
from app.ui.report_view import ReportView
from app.ui.history_view import HistoryView
from app.ui.settings_view import SettingsView
from app.ui.about_view import AboutView
from app.models.model_manager import model_manager
from app.utils.logger import add_log_listener
from app.utils.animations import fade_in
from app.utils import theme


class AppState:
    def __init__(self):
        self.before_path = None
        self.after_path = None
        self.preprocessed_tensor = None
        self.before_display = None
        self.after_display = None
        self.last_result = None
        self.last_metrics = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepSat-Change v1.0")
        self.resize(1536, 1024)
        self.app_state = AppState()

        model_manager.load()

        central = QWidget()
        self.setCentralWidget(central)
        outer_layout = QHBoxLayout(central)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.sidebar = Sidebar()
        outer_layout.addWidget(self.sidebar)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.header = Header()
        right_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack)
        outer_layout.addWidget(right_container, stretch=1)

        self.dashboard = Dashboard(self.app_state)
        self.upload_view = UploadView(self.app_state)
        self.preprocessing_view = PreprocessingView(self.app_state)
        self.prediction_view = PredictionView(self.app_state, on_result=self.on_prediction_result)
        self.results_view = ResultsView(self.app_state)
        self.visualization_view = VisualizationView(self.app_state)
        self.activation_view = ActivationMapsView(self.app_state)
        self.metrics_view = MetricsView(self.app_state)
        self.training_view = TrainingView(self.app_state)
        self.dataset_view = DatasetView(self.app_state)
        self.model_view = ModelView(self.app_state)
        self.report_view = ReportView(self.app_state)
        self.history_view = HistoryView(self.app_state)
        self.settings_view = SettingsView(self.app_state)
        self.about_view = AboutView(self.app_state)

        self.pages = {
            "dashboard": self.dashboard,
            "upload": self.upload_view,
            "preprocessing": self.preprocessing_view,
            "prediction": self.prediction_view,
            "results": self.results_view,
            "visualization": self.visualization_view,
            "activation": self.activation_view,
            "metrics": self.metrics_view,
            "training": self.training_view,
            "dataset": self.dataset_view,
            "model": self.model_view,
            "report": self.report_view,
            "history": self.history_view,
            "settings": self.settings_view,
            "about": self.about_view,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        self.sidebar.navigate.connect(self.navigate)
        self.sidebar.exit_requested.connect(self.close)
        self.navigate("dashboard")

        add_log_listener(self._on_log)

    def navigate(self, key):
        page = self.pages.get(key)
        if page is None:
            return
        self.sidebar.set_active(key)
        self.stack.setCurrentWidget(page)
        self._page_animation = fade_in(page, duration=220)
        if key == "dashboard":
            self.dashboard.refresh()
        elif key == "activation":
            self.activation_view.refresh_layers()
        elif key == "model":
            self.model_view.refresh()
        elif key == "history":
            self.history_view.refresh()

    def on_prediction_result(self, result):
        self.results_view.display_result(result)
        self.dashboard.set_images(
            result.before_display, result.after_display,
            (result.binary_mask * 255).astype("uint8"), result.overlay,
        )
        metrics = dict(result.change_stats)
        if self.app_state.last_metrics:
            metrics.update(self.app_state.last_metrics)
        self.dashboard.update_metrics(metrics)
        self.dashboard.workflow.complete_all()
        self.dashboard.overall_progress.setValue(100)
        self.navigate("results")

    def _on_log(self, level, message):
        try:
            self.dashboard.append_log(message)
        except Exception:
            pass
