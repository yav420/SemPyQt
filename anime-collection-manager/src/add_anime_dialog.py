import os
from PyQt6.QtWidgets import QDialog, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap
from PyQt6 import uic


class AddAnimeDialog(QDialog):
    def __init__(self, db, parent=None, anime_id=None):
        super().__init__(parent)
        self.db = db
        self.anime_id = anime_id
        self.poster_image = None

        ui_path = os.path.join(os.path.dirname(__file__), '..', 'qt', 'add_anime_dialog.ui')
        uic.loadUi(ui_path, self)

        self.genres = self.db.get_all_genres()

        self.setup_ui()
        self.setup_signals()

        if anime_id:
            self.load_anime_data()

    def setup_ui(self):
        # Загружаем список жанров
        self.combo_genre.clear()
        for genre in self.genres:
            self.combo_genre.addItem(genre['name'])

        # Добавляем пустой элемент
        self.combo_genre.addItem("Не указан")

        # Устанавливаем текущую дату
        today = QDate.currentDate()
        self.date_start.setDate(today)
        self.date_finish.setDate(today)

        # Настраиваем рейтинг (1-10)
        self.rating_buttons = {}
        for i in range(1, 11):
            button_name = f"radio_rating_{i}"
            if hasattr(self, button_name):
                self.rating_buttons[i] = getattr(self, button_name)

        # Связываем эпизоды
        self.spin_watched_episodes.valueChanged.connect(self.on_watched_episodes_changed)

    def setup_signals(self):
        """Настраивает сигналы и слоты"""
        self.btn_load_poster.clicked.connect(self.load_poster)
        self.btn_clear_poster.clicked.connect(self.clear_poster)
        self.buttonBox.accepted.connect(self.save_anime)
        self.buttonBox.rejected.connect(self.reject)

    def on_watched_episodes_changed(self, value):
        """Обрабатывает изменение количества просмотренных эпизодов"""
        total = self.spin_total_episodes.value()
        if total > 0 and value > total:
            self.spin_watched_episodes.setValue(total)

    def load_anime_data(self):
        """Загружает данные аниме для редактирования"""
        anime = self.db.get_anime(self.anime_id)
        if not anime:
            return

        # Заполняем поля
        self.edit_title.setText(anime['title'])
        self.edit_studio.setText(anime['studio'] or '')

        # Жанр
        genre_name = anime.get('genre_name', 'Не указан')
        index = self.combo_genre.findText(genre_name)
        if index >= 0:
            self.combo_genre.setCurrentIndex(index)

        # Тип
        index = self.combo_type.findText(anime['type'])
        if index >= 0:
            self.combo_type.setCurrentIndex(index)

        # Статус
        index = self.combo_status.findText(anime['status'])
        if index >= 0:
            self.combo_status.setCurrentIndex(index)

        # Даты
        if anime['start_date']:
            self.date_start.setDate(QDate.fromString(anime['start_date'], "yyyy-MM-dd"))
        if anime['finish_date']:
            self.date_finish.setDate(QDate.fromString(anime['finish_date'], "yyyy-MM-dd"))

        # Оценка
        if anime['rating'] and anime['rating'] in self.rating_buttons:
            self.rating_buttons[anime['rating']].setChecked(True)
            self.radio_rating_none.setChecked(False)
        else:
            self.radio_rating_none.setChecked(True)

        # Эпизоды
        self.spin_total_episodes.setValue(anime['total_episodes'] or 0)
        self.spin_watched_episodes.setValue(anime['watched_episodes'] or 0)

        # Отзыв
        self.text_review.setPlainText(anime['review'] or "")

        # Постер
        if anime['poster_image']:
            self.poster_image = anime['poster_image']
            self.update_poster_preview()

    def load_poster(self):
        """Загружает постер аниме"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.poster_image = f.read()
                self.update_poster_preview()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {e}")

    def clear_poster(self):
        """Очищает постер"""
        self.poster_image = None
        self.lbl_poster_preview.clear()
        self.lbl_poster_preview.setText("Постер не загружен")

    def update_poster_preview(self):
        """Обновляет превью постера"""
        if self.poster_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.poster_image)
            scaled_pixmap = pixmap.scaled(180, 250, Qt.AspectRatioMode.KeepAspectRatio)
            self.lbl_poster_preview.setPixmap(scaled_pixmap)

    def validate_input(self):
        """Проверяет корректность введенных данных"""
        title = self.edit_title.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название аниме")
            return False

        watched = self.spin_watched_episodes.value()
        total = self.spin_total_episodes.value()

        if watched > total:
            QMessageBox.warning(self, "Ошибка", "Просмотренных эпизодов не может быть больше общего количества")
            return False

        return True

    def save_anime(self):
        """Сохраняет аниме в базу данных"""
        if not self.validate_input():
            return

        # Собираем данные
        anime_data = {
            'title': self.edit_title.text().strip(),
            'studio': self.edit_studio.text().strip(),
            'genre': self.combo_genre.currentText() if self.combo_genre.currentText() != "Не указан" else None,
            'type': self.combo_type.currentText(),
            'status': self.combo_status.currentText(),
            'start_date': self.date_start.date().toString("yyyy-MM-dd"),
            'finish_date': self.date_finish.date().toString("yyyy-MM-dd"),
            'review': self.text_review.toPlainText().strip(),
            'poster_image': self.poster_image,
            'total_episodes': self.spin_total_episodes.value(),
            'watched_episodes': self.spin_watched_episodes.value()
        }

        # Определяем рейтинг
        anime_data['rating'] = None
        for rating, button in self.rating_buttons.items():
            if button.isChecked():
                anime_data['rating'] = rating
                break

        try:
            if self.anime_id:
                # Редактируем существующее аниме
                success = self.db.update_anime(self.anime_id, anime_data)
                if not success:
                    raise Exception("Не удалось обновить аниме")
            else:
                # Добавляем новое аниме
                anime_id = self.db.add_anime(anime_data)
                if not anime_id:
                    raise Exception("Не удалось добавить аниме")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")