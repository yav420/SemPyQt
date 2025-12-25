import os
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QInputDialog,
    QTableWidgetItem, QMenu, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QPixmap, QShortcut, QKeySequence
from PyQt6 import uic
from add_anime_dialog import AddAnimeDialog
from statistics_dialog import StatisticsDialog
import csv


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_anime_id = None

        # Загружаем интерфейс из файла .ui
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'qt', 'main_window.ui')
        uic.loadUi(ui_path, self)

        self.setup_ui()
        self.setup_signals()
        self.load_anime()

    def setup_ui(self):
        """Настраивает интерфейс"""
        # Настраиваем таблицу аниме
        headers = ["ID", "Название", "Студия", "Жанр", "Тип", "Статус", "Начало", "Конец", "Оценка", "Эпизоды"]
        self.table_anime.setColumnCount(len(headers))
        self.table_anime.setHorizontalHeaderLabels(headers)

        # Настраиваем ширину колонок
        self.table_anime.hideColumn(0)  # Скрываем ID
        self.table_anime.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_anime.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_anime.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_anime.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_anime.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Устанавливаем заголовки для детальной информации
        self.lbl_poster.setText("")

        # Настраиваем цветовые стили для статус бара
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #f1f2f6;
                color: #2f3542;
                font-weight: bold;
            }
        """)

    def setup_signals(self):
        """Настраивает сигналы и слоты"""
        # Кнопки
        self.btn_add.clicked.connect(self.add_anime)
        self.btn_edit.clicked.connect(self.edit_anime)
        self.btn_delete.clicked.connect(self.delete_anime)
        self.btn_stats.clicked.connect(self.show_statistics)
        self.btn_export.clicked.connect(self.export_data)

        # Поиск
        self.search_input.textChanged.connect(self.load_anime)

        # Таблица
        self.table_anime.currentCellChanged.connect(self.on_anime_selected)
        self.table_anime.customContextMenuRequested.connect(self.show_context_menu)
        self.table_anime.doubleClicked.connect(self.edit_anime)

        # Меню
        self.action_new.triggered.connect(self.add_anime)
        self.action_edit.triggered.connect(self.edit_anime)
        self.action_delete.triggered.connect(self.delete_anime)
        self.action_export.triggered.connect(self.export_data)
        self.action_import.triggered.connect(self.import_data)
        self.action_stats.triggered.connect(self.show_statistics)
        self.action_about.triggered.connect(self.show_about)
        self.action_exit.triggered.connect(self.close)

        # Горячие клавиши
        shortcut_add = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_add.activated.connect(self.add_anime)

        shortcut_edit = QShortcut(QKeySequence("Ctrl+E"), self)
        shortcut_edit.activated.connect(self.edit_anime)

        shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        shortcut_delete.activated.connect(self.delete_anime)

        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.focus_search)

    def focus_search(self):
        """Переводит фокус на поле поиска"""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def load_anime(self):
        """Загружает список аниме в таблицу"""
        search_text = self.search_input.text().strip()
        anime_list = self.db.get_all_anime(search_text)

        self.table_anime.setRowCount(len(anime_list))

        for row, anime in enumerate(anime_list):
            # ID
            self.table_anime.setItem(row, 0, QTableWidgetItem(str(anime['id'])))

            # Название
            title_item = QTableWidgetItem(anime['title'])
            title_item.setToolTip(anime['title'])
            self.table_anime.setItem(row, 1, title_item)

            # Студия
            studio_item = QTableWidgetItem(anime['studio'] or 'Не указана')
            studio_item.setToolTip(anime['studio'] or '')
            self.table_anime.setItem(row, 2, studio_item)

            # Жанр
            genre = anime.get('genre_name', 'Не указан')
            genre_item = QTableWidgetItem(genre)
            genre_item.setToolTip(genre)
            self.table_anime.setItem(row, 3, genre_item)

            # Тип
            type_item = QTableWidgetItem(anime['type'])
            type_item.setToolTip(anime['type'])
            self.table_anime.setItem(row, 4, type_item)

            # Статус
            status_item = QTableWidgetItem(anime['status'])
            # Раскрашиваем статусы
            if anime['status'] == 'Просмотрено':
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif anime['status'] == 'Смотрю':
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif anime['status'] == 'Запланировано':
                status_item.setBackground(Qt.GlobalColor.blue)
                status_item.setForeground(Qt.GlobalColor.white)
            elif anime['status'] == 'Отложено':
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            elif anime['status'] == 'Брошено':
                status_item.setBackground(Qt.GlobalColor.gray)
                status_item.setForeground(Qt.GlobalColor.white)

            status_item.setToolTip(anime['status'])
            self.table_anime.setItem(row, 5, status_item)

            # Дата начала
            start_date = anime['start_date'] or ''
            start_item = QTableWidgetItem(start_date)
            start_item.setToolTip(start_date)
            self.table_anime.setItem(row, 6, start_item)

            # Дата окончания
            finish_date = anime['finish_date'] or ''
            finish_item = QTableWidgetItem(finish_date)
            finish_item.setToolTip(finish_date)
            self.table_anime.setItem(row, 7, finish_item)

            # Оценка
            rating = anime['rating'] or ''
            if rating:
                rating_item = QTableWidgetItem(str(rating))
                rating_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                rating_item.setToolTip(f"Оценка: {rating}/10")

                # Цвет оценки в зависимости от значения
                if rating >= 9:
                    rating_item.setForeground(Qt.GlobalColor.darkGreen)
                elif rating >= 7:
                    rating_item.setForeground(Qt.GlobalColor.green)
                elif rating >= 5:
                    rating_item.setForeground(Qt.GlobalColor.darkYellow)
                else:
                    rating_item.setForeground(Qt.GlobalColor.red)

                self.table_anime.setItem(row, 8, rating_item)
            else:
                rating_item = QTableWidgetItem('')
                rating_item.setToolTip('Нет оценки')
                self.table_anime.setItem(row, 8, rating_item)

            # Эпизоды
            watched = anime.get('watched_episodes', 0) or 0
            total = anime.get('total_episodes', 0) or 0
            if total > 0:
                episodes_text = f"{watched}/{total}"
                percent = (watched / total * 100) if total > 0 else 0
                episodes_item = QTableWidgetItem(episodes_text)
                episodes_item.setToolTip(f"Просмотрено: {watched} из {total} ({percent:.1f}%)")

                # Цвет прогресса
                if percent == 100:
                    episodes_item.setForeground(Qt.GlobalColor.darkGreen)
                elif percent >= 50:
                    episodes_item.setForeground(Qt.GlobalColor.darkBlue)
                else:
                    episodes_item.setForeground(Qt.GlobalColor.darkRed)

            else:
                episodes_item = QTableWidgetItem(str(watched))
                episodes_item.setToolTip(f"Просмотрено эпизодов: {watched}")

            self.table_anime.setItem(row, 9, episodes_item)

        # Обновляем статус бар
        total_count = len(anime_list)
        if search_text:
            self.statusbar.showMessage(f"Найдено аниме: {total_count} (поиск: '{search_text}')", 5000)
        else:
            self.statusbar.showMessage(f"Всего аниме: {total_count}")

    def on_anime_selected(self, current_row, current_column, previous_row, previous_column):
        """Обрабатывает выбор аниме в таблице"""
        if current_row < 0:  # Если строка не выбрана
            return

        anime_id_item = self.table_anime.item(current_row, 0)
        if not anime_id_item:
            return

        anime_id = int(anime_id_item.text())
        self.current_anime_id = anime_id

        # Загружаем детальную информацию
        anime = self.db.get_anime(anime_id)
        if anime:
            self.show_anime_details(anime)

    def show_anime_details(self, anime):
        """Показывает детальную информацию об аниме"""
        # Основная информация
        self.lbl_title.setText(anime['title'])
        self.lbl_studio.setText(anime['studio'] or 'Не указана')
        self.lbl_genre.setText(anime.get('genre_name', 'Не указан'))
        self.lbl_type.setText(anime['type'])

        # Даты
        dates = []
        if anime['start_date']:
            dates.append(f"Начало: {anime['start_date']}")
        if anime['finish_date']:
            dates.append(f"Окончание: {anime['finish_date']}")
        self.lbl_dates.setText("\n".join(dates) if dates else "Не указаны")

        # Оценка
        if anime['rating']:
            rating_text = f"{anime['rating']}/10"
            self.lbl_rating.setText(rating_text)
        else:
            self.lbl_rating.setText("Нет оценки")

        # Статус
        status_text = anime['status']
        self.lbl_status.setText(status_text)

        # Эпизоды
        watched = anime.get('watched_episodes', 0) or 0
        total = anime.get('total_episodes', 0) or 0
        if total > 0:
            percent = (watched / total * 100) if total > 0 else 0
            episodes_text = f"{watched}/{total} ({percent:.1f}%)"
        else:
            episodes_text = str(watched)
        self.lbl_episodes.setText(episodes_text)

        # Отзыв
        review_text = anime['review'] or "Нет отзыва"
        self.text_review.setText(review_text)

        # Постер
        if anime['poster_image']:
            pixmap = QPixmap()
            if pixmap.loadFromData(anime['poster_image']):
                scaled_pixmap = pixmap.scaled(220, 320, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.lbl_poster.setPixmap(scaled_pixmap)
            else:
                self.lbl_poster.setText("Ошибка загрузки изображения")
        else:
            self.lbl_poster.setText("Нет постера")

    def add_anime(self):
        """Добавляет новое аниме"""
        dialog = AddAnimeDialog(self.db, self)
        if dialog.exec():
            self.load_anime()
            self.statusbar.showMessage("✅ Аниме успешно добавлено", 3000)

    def edit_anime(self):
        """Редактирует выбранное аниме"""
        if not self.current_anime_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите аниме для редактирования")
            return

        dialog = AddAnimeDialog(self.db, self, self.current_anime_id)
        if dialog.exec():
            self.load_anime()
            self.statusbar.showMessage("✅ Аниме успешно обновлено", 3000)

    def delete_anime(self):
        """Удаляет выбранное аниме"""
        if not self.current_anime_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите аниме для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить это аниме?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_anime(self.current_anime_id):
                self.current_anime_id = None
                self.load_anime()
                self.statusbar.showMessage("✅ Аниме успешно удалено", 3000)
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить аниме")

    def show_statistics(self):
        """Показывает диалог статистики"""
        dialog = StatisticsDialog(self.db, self)
        dialog.exec()

    def export_data(self):
        """Экспортирует данные в CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт данных", "anime_collection.csv", "CSV Files (*.csv)"
        )

        if file_path:
            if self.db.export_to_csv(file_path):
                QMessageBox.information(self, "Успех",
                                        f"✅ Данные успешно экспортированы в:\n{file_path}")
            else:
                QMessageBox.critical(self, "Ошибка",
                                     "❌ Не удалось экспортировать данные")

    def import_data(self):
        """Импортирует данные из CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт данных", "", "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            imported_count = 0
            skipped_count = 0
            errors = []

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                if not reader.fieldnames:
                    QMessageBox.critical(self, "Ошибка", "CSV файл пустой или поврежден")
                    return

                # Проверяем обязательные поля
                required_fields = ['title', 'status']
                missing_fields = [field for field in required_fields if field not in reader.fieldnames]

                if missing_fields:
                    QMessageBox.critical(self, "Ошибка",
                                         f"В CSV файле отсутствуют обязательные поля: {', '.join(missing_fields)}")
                    return

                total_rows = 0
                rows = []
                for row in reader:
                    rows.append(row)
                    total_rows += 1

                # Показываем прогресс для больших файлов
                if total_rows > 10:
                    progress_dialog = QInputDialog(self)
                    progress_dialog.setWindowTitle("Импорт данных")
                    progress_dialog.setLabelText(f"Импортируется {total_rows} записей...")
                    progress_dialog.setCancelButtonText("Отмена")
                    progress_dialog.show()

                for i, row in enumerate(rows):
                    try:
                        # Очищаем и проверяем данные
                        title = row.get('title', '').strip()
                        if not title:
                            errors.append(f"Строка {i + 2}: Отсутствует название")
                            skipped_count += 1
                            continue

                        # Проверяем статус
                        status = row.get('status', 'Запланировано').strip()
                        valid_statuses = ['Запланировано', 'Смотрю', 'Просмотрено', 'Отложено', 'Брошено']
                        if status not in valid_statuses:
                            status = 'Запланировано'  # Значение по умолчанию

                        # Обрабатываем рейтинг
                        rating_str = row.get('rating', '').strip()
                        rating = None
                        if rating_str and rating_str.isdigit():
                            rating_int = int(rating_str)
                            if 1 <= rating_int <= 10:
                                rating = rating_int

                        # Обрабатываем эпизоды
                        total_episodes_str = row.get('total_episodes', '0').strip()
                        watched_episodes_str = row.get('watched_episodes', '0').strip()

                        total_episodes = 0
                        if total_episodes_str.isdigit():
                            total_episodes = int(total_episodes_str)

                        watched_episodes = 0
                        if watched_episodes_str.isdigit():
                            watched_episodes = int(watched_episodes_str)

                        # Проверяем, что watched не больше total
                        if watched_episodes > total_episodes:
                            watched_episodes = total_episodes

                        # Обрабатываем даты
                        start_date = row.get('start_date', '').strip() or None
                        finish_date = row.get('finish_date', '').strip() or None

                        # Преобразуем данные
                        anime_data = {
                            'title': title,
                            'studio': row.get('studio', '').strip(),
                            'genre': row.get('genre', '').strip() or None,
                            'type': row.get('type', 'TV Сериал').strip(),
                            'status': status,
                            'start_date': start_date,
                            'finish_date': finish_date,
                            'rating': rating,
                            'total_episodes': total_episodes,
                            'watched_episodes': watched_episodes,
                            'review': row.get('review', '').strip(),
                            'poster_image': None  # Постеры из CSV не импортируем
                        }

                        # Добавляем в базу
                        anime_id = self.db.add_anime(anime_data)
                        if anime_id:
                            imported_count += 1
                        else:
                            errors.append(f"Строка {i + 2}: Не удалось добавить в базу данных")
                            skipped_count += 1

                    except Exception as e:
                        errors.append(f"Строка {i + 2}: {str(e)}")
                        skipped_count += 1
                        continue

            # Показываем результаты импорта
            result_message = f"✅ Импорт завершен!\n\n"
            result_message += f"Успешно импортировано: {imported_count}\n"
            result_message += f"Пропущено: {skipped_count}\n"

            if errors:
                result_message += f"\nОшибки ({len(errors)}):\n"
                result_message += "\n".join(errors[:5])  # Показываем первые 5 ошибок
                if len(errors) > 5:
                    result_message += f"\n... и еще {len(errors) - 5} ошибок"

                # Сохраняем ошибки в файл
                error_file = file_path.replace('.csv', '_errors.txt')
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(errors))
                result_message += f"\n\nПолный список ошибок сохранен в:\n{error_file}"

            QMessageBox.information(self, "Результат импорта", result_message)

            # Обновляем список аниме
            if imported_count > 0:
                self.load_anime()

        except UnicodeDecodeError:
            QMessageBox.critical(self, "Ошибка",
                                 "Невозможно прочитать файл. Убедитесь, что файл сохранен в кодировке UTF-8.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Ошибка при импорте данных:\n{str(e)}")

    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """
        <h2 style="color: #ff6b8b;">🎌 Аниме-менеджер</h2>
        <p><b>Версия 1.1.0</b></p>

        <p>Программа для ведения учета просмотренных аниме.</p>

        <p><b>✨ Возможности:</b></p>
        <ul>
            <li>📝 Добавление и редактирование аниме</li>
            <li>📊 Отслеживание прогресса просмотра</li>
            <li>💬 Ведение отзывов и заметок</li>
            <li>🖼️ Загрузка постеров</li>
            <li>📈 Статистика просмотра с графиками</li>
            <li>📤 Экспорт данных в CSV</li>
            <li>📥 Импорт данных из CSV</li>
            <li>🔍 Поиск по названию и студии</li>
            <li>🎨 Цветовое кодирование статусов</li>
        </ul>

        <p><b>📋 Поддерживаемые типы:</b> TV Сериал, Фильм, OVA/OAD, ONA, Спешл</p>
        <p><b>🏷️ Поддерживаемые статусы:</b> Запланировано, Смотрю, Просмотрено, Отложено, Брошено</p>

        <hr>
        <p style="color: #666;">© 2024 Аниме-менеджер | Сделано с ❤️ для отаку</p>
        <p style="font-size: 10px; color: #999;">Использует: PyQt6, SQLite, Matplotlib</p>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("О программе")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(QPixmap())  # Пустая иконка
        msg_box.exec()

    def show_context_menu(self, position):
        """Показывает контекстное меню для таблицы"""
        # Получаем элемент по позиции
        item = self.table_anime.itemAt(position)
        if item:
            # Выделяем строку, на которой было вызвано меню
            self.table_anime.selectRow(item.row())
        else:
            # Если кликнули на пустое место, снимаем выделение
            self.table_anime.clearSelection()
            self.current_anime_id = None

        menu = QMenu()

        add_action = menu.addAction("➕ Добавить аниме")
        edit_action = menu.addAction("✏️ Редактировать")
        delete_action = menu.addAction("❌ Удалить")
        menu.addSeparator()
        view_details_action = menu.addAction("👁️ Просмотреть детали")
        mark_watched_action = menu.addAction("✅ Отметить как просмотренное")
        menu.addSeparator()
        export_action = menu.addAction("📤 Экспорт выделенного")

        # Делаем действия недоступными если ничего не выбрано
        if not self.current_anime_id:
            edit_action.setEnabled(False)
            delete_action.setEnabled(False)
            view_details_action.setEnabled(False)
            mark_watched_action.setEnabled(False)
            export_action.setEnabled(False)

        action = menu.exec(self.table_anime.mapToGlobal(position))

        if action == add_action:
            self.add_anime()
        elif action == edit_action:
            self.edit_anime()
        elif action == delete_action:
            self.delete_anime()
        elif action == view_details_action:
            # Переключаемся на вкладку с деталями
            self.tabWidget.setCurrentIndex(1)
        elif action == mark_watched_action and self.current_anime_id:
            self.mark_as_watched()
        elif action == export_action and self.current_anime_id:
            self.export_selected()

    def mark_as_watched(self):
        """Отмечает выбранное аниме как просмотренное"""
        if not self.current_anime_id:
            return

        anime = self.db.get_anime(self.current_anime_id)
        if not anime:
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Отметить '{anime['title']}' как просмотренное?\n"
            f"Все эпизоды будут отмечены как просмотренные.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Обновляем данные
                update_data = {
                    'title': anime['title'],
                    'studio': anime['studio'] or '',
                    'genre': anime.get('genre_name'),
                    'type': anime['type'],
                    'status': 'Просмотрено',
                    'start_date': anime['start_date'] or QDate.currentDate().toString("yyyy-MM-dd"),
                    'finish_date': QDate.currentDate().toString("yyyy-MM-dd"),
                    'rating': anime['rating'],
                    'review': anime['review'] or '',
                    'poster_image': anime.get('poster_image'),
                    'total_episodes': anime.get('total_episodes', 0) or 0,
                    'watched_episodes': anime.get('total_episodes', 0) or 0
                }

                self.db.update_anime(self.current_anime_id, update_data)
                self.load_anime()
                self.statusbar.showMessage(f"✅ '{anime['title']}' отмечено как просмотренное", 3000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус: {str(e)}")

    def export_selected(self):
        """Экспортирует выбранное аниме в отдельный CSV файл"""
        if not self.current_anime_id:
            return

        anime = self.db.get_anime(self.current_anime_id)
        if not anime:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт аниме", f"{anime['title'].replace(' ', '_')}.csv", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['title', 'studio', 'genre', 'type', 'status',
                                  'start_date', 'finish_date', 'rating',
                                  'total_episodes', 'watched_episodes', 'review']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerow({
                        'title': anime['title'],
                        'studio': anime['studio'] or '',
                        'genre': anime.get('genre_name', ''),
                        'type': anime['type'],
                        'status': anime['status'],
                        'start_date': anime['start_date'] or '',
                        'finish_date': anime['finish_date'] or '',
                        'rating': anime['rating'] or '',
                        'total_episodes': anime.get('total_episodes', 0) or 0,
                        'watched_episodes': anime.get('watched_episodes', 0) or 0,
                        'review': anime['review'] or ''
                    })

                QMessageBox.information(self, "Успех",
                                        f"✅ Аниме '{anime['title']}' экспортировано в:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"❌ Не удалось экспортировать:\n{str(e)}")

    def closeEvent(self, event):
        """Обрабатывает закрытие окна"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()