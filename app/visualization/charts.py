import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from app.utils import theme

plt.rcParams["figure.facecolor"] = theme.BG_PANEL
plt.rcParams["axes.facecolor"] = theme.BG_PANEL
plt.rcParams["axes.edgecolor"] = theme.BORDER
plt.rcParams["text.color"] = theme.TEXT_PRIMARY
plt.rcParams["axes.labelcolor"] = theme.TEXT_SECONDARY
plt.rcParams["xtick.color"] = theme.TEXT_SECONDARY
plt.rcParams["ytick.color"] = theme.TEXT_SECONDARY
plt.rcParams["grid.color"] = theme.BORDER


class LineChartCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=3):
        self.fig = Figure(figsize=(width, height), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self._style_axis()

    def _style_axis(self):
        self.ax.set_facecolor(theme.BG_PANEL)
        self.ax.grid(True, alpha=0.2)
        for spine in self.ax.spines.values():
            spine.set_color(theme.BORDER)

    def plot_series(self, series_dict, xlabel="Epoch", ylabel="Value"):
        self.ax.clear()
        self._style_axis()
        colors = [theme.ACCENT_PURPLE, theme.ACCENT_CYAN, theme.WARNING, theme.SUCCESS]
        for i, (label, values) in enumerate(series_dict.items()):
            self.ax.plot(values, label=label, color=colors[i % len(colors)], linewidth=1.8)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        if series_dict:
            self.ax.legend(facecolor=theme.BG_PANEL_LIGHT, edgecolor=theme.BORDER, labelcolor=theme.TEXT_PRIMARY, fontsize=8)
        self.fig.tight_layout()
        self.draw()


class DonutChartCanvas(FigureCanvasQTAgg):
    def __init__(self, width=3, height=3):
        self.fig = Figure(figsize=(width, height), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

    def plot(self, changed_pct, unchanged_pct):
        self.ax.clear()
        colors = [theme.ERROR, theme.BORDER]
        wedges, _ = self.ax.pie(
            [changed_pct, unchanged_pct],
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.35, edgecolor=theme.BG_PANEL),
        )
        self.ax.set_aspect("equal")
        self.fig.tight_layout()
        self.draw()


class ConfusionMatrixCanvas(FigureCanvasQTAgg):
    def __init__(self, width=4, height=4):
        self.fig = Figure(figsize=(width, height), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

    def plot(self, tp, tn, fp, fn):
        import numpy as np
        self.ax.clear()
        matrix = np.array([[tn, fp], [fn, tp]])
        self.ax.imshow(matrix, cmap="Purples")
        labels = [["TN", "FP"], ["FN", "TP"]]
        for i in range(2):
            for j in range(2):
                self.ax.text(j, i, f"{labels[i][j]}\n{matrix[i][j]}", ha="center", va="center", color=theme.TEXT_PRIMARY)
        self.ax.set_xticks([0, 1])
        self.ax.set_yticks([0, 1])
        self.ax.set_xticklabels(["NO CHANGE", "CHANGE"])
        self.ax.set_yticklabels(["NO CHANGE", "CHANGE"])
        self.ax.set_xlabel("PREDICTED")
        self.ax.set_ylabel("ACTUAL")
        self.fig.tight_layout()
        self.draw()
