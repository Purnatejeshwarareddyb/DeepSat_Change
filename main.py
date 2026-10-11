import sys
from PySide6.QtWidgets import QApplication
from app.utils.logger import log
from app.utils import theme
from app.ui.main_window import MainWindow


def main():
    log.info("DeepSat-Change starting")
    app = QApplication(sys.argv)
    app.setStyleSheet(theme.STYLESHEET)
    window = MainWindow()
    window.show()
    log.info("Interface ready")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
