from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect


def fade_in(widget, duration=220, parent_holder=None):
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    if parent_holder is not None:
        parent_holder.append(animation)
    animation.start(QAbstractAnimation.DeleteWhenStopped)
    return animation


def animate_progress_value(progress_bar, target_value, duration=300):
    animation = QPropertyAnimation(progress_bar, b"value", progress_bar)
    animation.setDuration(duration)
    animation.setStartValue(progress_bar.value())
    animation.setEndValue(target_value)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start(QAbstractAnimation.DeleteWhenStopped)
    return animation


class CountUpAnimator:
    def __init__(self, label, duration=500, steps=20):
        self.label = label
        self.duration = duration
        self.steps = steps

    def animate_to(self, target_value, is_percent=False, decimals=0):
        from PySide6.QtCore import QTimer
        start = 0
        step_ms = max(1, self.duration // self.steps)
        state = {"i": 0}

        def tick():
            state["i"] += 1
            progress = state["i"] / self.steps
            value = start + (target_value - start) * progress
            text = f"{value:.{decimals}f}"
            if is_percent:
                text += "%"
            self.label.setText(text)
            if state["i"] >= self.steps:
                timer.stop()

        timer = QTimer(self.label)
        timer.timeout.connect(tick)
        timer.start(step_ms)
        return timer
