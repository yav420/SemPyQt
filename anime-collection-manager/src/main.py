import sys
import os
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from database import Database


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Аниме-менеджер")

    # Устанавливаем стиль
    app.setStyle("Fusion")

    db = Database()
    db.init_db()

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()