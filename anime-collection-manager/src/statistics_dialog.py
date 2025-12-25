import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidgetItem, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import uic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime


class StatisticsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db

        # Загружаем интерфейс
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'qt', 'statistics_dialog.ui')
        uic.loadUi(ui_path, self)

        self.setup_ui()
        self.load_statistics()

    def setup_ui(self):
        """Настраивает интерфейс"""
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Настраиваем таблицы
        self.table_genres.setColumnCount(3)
        self.table_genres.setHorizontalHeaderLabels(["Жанр", "Количество", "%"])

        self.table_ratings.setColumnCount(2)
        self.table_ratings.setHorizontalHeaderLabels(["Оценка", "Количество"])

        self.table_types.setColumnCount(2)
        self.table_types.setHorizontalHeaderLabels(["Тип", "Количество"])

    def load_statistics(self):
        """Загружает статистику"""
        try:
            stats = self.db.get_statistics()

            # Общая статистика
            self.lbl_total_anime.setText(str(stats.get('total', 0)))
            self.lbl_watched_anime.setText(str(stats.get('watched_count', 0)))
            self.lbl_watching_anime.setText(str(stats.get('watching_count', 0)))
            self.lbl_planned_anime.setText(str(stats.get('planned_count', 0)))
            self.lbl_dropped_anime.setText(str(stats.get('dropped_count', 0)))
            self.lbl_avg_rating.setText(str(stats.get('avg_rating', 0)))

            # Эпизоды
            total_eps = stats.get('total_episodes', 0)
            watched_eps = stats.get('watched_episodes', 0)
            self.lbl_total_episodes.setText(str(total_eps))

            if total_eps > 0:
                percent = (watched_eps / total_eps * 100) if total_eps > 0 else 0
                self.lbl_watched_episodes.setText(f"{watched_eps} ({percent:.1f}%)")
            else:
                self.lbl_watched_episodes.setText(str(watched_eps))

            # Средняя длительность (примерно: 24 мин на эпизод)
            total_minutes = watched_eps * 24
            if watched_eps > 0:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                self.lbl_avg_duration.setText(f"{hours}ч {minutes}мин")
            else:
                self.lbl_avg_duration.setText("0ч 0мин")

            # Аниме в этом году - упрощенный расчет
            current_year = datetime.now().year
            monthly_stats = stats.get('monthly_stats', [])
            anime_this_year = 0

            for stat in monthly_stats:
                month = stat.get('month', '')
                if month.startswith(str(current_year)):
                    anime_this_year += stat.get('count', 0)

            self.lbl_anime_this_year.setText(str(anime_this_year))

            # График просмотра по месяцам
            self.create_monthly_chart(monthly_stats)

            # Статистика по жанрам
            self.load_genres_stats(stats.get('genres_stats', []))

            # Статистика по оценкам
            self.load_ratings_stats(stats.get('ratings_stats', []))

            # Статистика по типам
            self.load_types_stats(stats.get('types_stats', []))

        except Exception as e:
            print(f"Ошибка при загрузке статистики: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить статистику:\n{str(e)}")

    def create_monthly_chart(self, monthly_stats):
        """Создает график просмотра по месяцам"""
        # Очищаем предыдущий график
        for i in reversed(range(self.widget_chart.layout().count() if self.widget_chart.layout() else 0)):
            widget = self.widget_chart.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not monthly_stats:
            layout = QVBoxLayout(self.widget_chart)
            label = QLabel("Нет данных для графика")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return

        # Создаем график
        fig = Figure(figsize=(7, 4))
        canvas = FigureCanvas(fig)

        ax = fig.add_subplot(111)

        # Подготавливаем данные
        months = [item.get('month', '') for item in monthly_stats[-12:]]  # Последние 12 месяцев
        counts = [item.get('count', 0) for item in monthly_stats[-12:]]

        # Используем пастельные цвета для аниме-темы
        bars = ax.bar(range(len(months)), counts, color='#ff6b8b', edgecolor='#ff4757', linewidth=1.5)

        ax.set_xlabel('Месяц', fontsize=10, fontweight='bold')
        ax.set_ylabel('Количество аниме', fontsize=10, fontweight='bold')
        ax.set_title('Активность просмотра по месяцам', fontsize=12, fontweight='bold', color='#2f3542')

        # Устанавливаем цвет фона
        ax.set_facecolor('#f1f2f6')
        fig.patch.set_facecolor('#f1f2f6')

        if len(months) <= 12:
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, rotation=45, fontsize=9)
        else:
            ax.set_xticks(range(0, len(months), 2))
            ax.set_xticklabels(months[::2], rotation=45, fontsize=9)

        # Добавляем сетку
        ax.grid(True, alpha=0.3, linestyle='--')

        if len(bars) <= 15:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{int(height)}', ha='center', va='bottom',
                            fontsize=9, fontweight='bold')

        fig.tight_layout()

        layout = QVBoxLayout(self.widget_chart)
        layout.addWidget(canvas)

    def load_genres_stats(self, genres_stats):
        """Загружает статистику по жанрам"""
        total = sum(item.get('count', 0) for item in genres_stats)

        self.table_genres.setRowCount(len(genres_stats))

        row = 0
        for genre_stat in genres_stats:
            genre = genre_stat.get('genre', '')
            count = genre_stat.get('count', 0)

            if count == 0:
                continue

            percentage = (count / total * 100) if total > 0 else 0

            self.table_genres.setItem(row, 0, QTableWidgetItem(genre))
            self.table_genres.setItem(row, 1, QTableWidgetItem(str(count)))
            self.table_genres.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
            row += 1

        self.create_pie_chart(genres_stats)

    def create_pie_chart(self, genres_stats):
        """Создает круговую диаграмму по жанрам"""
        for i in reversed(range(self.widget_pie_chart.layout().count() if self.widget_pie_chart.layout() else 0)):
            widget = self.widget_pie_chart.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        filtered_stats = [item for item in genres_stats if item.get('count', 0) > 0]
        if not filtered_stats:
            layout = QVBoxLayout(self.widget_pie_chart)
            label = QLabel("Нет данных для диаграммы")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return

        labels = [item.get('genre', '') for item in filtered_stats]
        sizes = [item.get('count', 0) for item in filtered_stats]

        fig = Figure(figsize=(5.5, 5))
        canvas = FigureCanvas(fig)

        ax = fig.add_subplot(111)

        # Яркие цвета для аниме-темы
        colors = plt.cm.Set3([i / len(filtered_stats) for i in range(len(filtered_stats))])

        wedges, texts, autotexts = ax.pie(sizes,
                                          labels=labels,
                                          autopct='%1.1f%%',
                                          startangle=90,
                                          colors=colors,
                                          textprops={'fontsize': 8})

        ax.set_title('Распределение по жанрам', fontsize=11, fontweight='bold', color='#2f3542')
        ax.set_facecolor('#f1f2f6')
        fig.patch.set_facecolor('#f1f2f6')

        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        for text in texts:
            text.set_fontsize(9)

        fig.tight_layout()

        layout = QVBoxLayout(self.widget_pie_chart)
        layout.addWidget(canvas)

    def load_ratings_stats(self, ratings_stats):
        """Загружает статистику по оценкам"""
        self.table_ratings.setRowCount(len(ratings_stats))

        for row, rating_stat in enumerate(ratings_stats):
            rating = rating_stat.get('rating', 0)
            count = rating_stat.get('count', 0)

            self.table_ratings.setItem(row, 0, QTableWidgetItem(str(rating)))
            self.table_ratings.setItem(row, 1, QTableWidgetItem(str(count)))

        self.create_bar_chart(ratings_stats)

    def create_bar_chart(self, ratings_stats):
        """Создает столбчатую диаграмму оценок"""
        for i in reversed(range(self.widget_bar_chart.layout().count() if self.widget_bar_chart.layout() else 0)):
            widget = self.widget_bar_chart.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not ratings_stats:
            layout = QVBoxLayout(self.widget_bar_chart)
            label = QLabel("Нет данных для графика")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return

        ratings = [item.get('rating', 0) for item in ratings_stats]
        counts = [item.get('count', 0) for item in ratings_stats]
        labels = [str(r) for r in ratings]

        fig = Figure(figsize=(5.5, 5))
        canvas = FigureCanvas(fig)

        ax = fig.add_subplot(111)

        # Градиент от зеленого к красному в зависимости от оценки
        colors = []
        for rating in ratings:
            if rating >= 7:
                colors.append('#2ed573')  # зеленый для высоких оценок
            elif rating >= 5:
                colors.append('#ffa502')  # оранжевый для средних
            else:
                colors.append('#ff4757')  # красный для низких

        bars = ax.bar(labels, counts, color=colors, edgecolor='#2f3542', linewidth=1.2)

        ax.set_xlabel('Оценка', fontsize=10, fontweight='bold')
        ax.set_ylabel('Количество аниме', fontsize=10, fontweight='bold')
        ax.set_title('Распределение оценок', fontsize=11, fontweight='bold', color='#2f3542')
        ax.set_facecolor('#f1f2f6')
        fig.patch.set_facecolor('#f1f2f6')

        # Добавляем сетку
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

        fig.tight_layout()

        layout = QVBoxLayout(self.widget_bar_chart)
        layout.addWidget(canvas)

    def load_types_stats(self, types_stats):
        """Загружает статистику по типам аниме"""
        if not types_stats:
            return

        self.table_types.setRowCount(len(types_stats))

        for row, type_stat in enumerate(types_stats):
            anime_type = type_stat.get('type', '')
            count = type_stat.get('count', 0)

            self.table_types.setItem(row, 0, QTableWidgetItem(anime_type))
            self.table_types.setItem(row, 1, QTableWidgetItem(str(count)))

        self.create_types_chart(types_stats)

    def create_types_chart(self, types_stats):
        """Создает диаграмму по типам аниме"""
        for i in reversed(range(self.widget_types_chart.layout().count() if self.widget_types_chart.layout() else 0)):
            widget = self.widget_types_chart.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not types_stats:
            layout = QVBoxLayout(self.widget_types_chart)
            label = QLabel("Нет данных для диаграммы")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return

        types = [item.get('type', '') for item in types_stats]
        counts = [item.get('count', 0) for item in types_stats]

        fig = Figure(figsize=(5.5, 5))
        canvas = FigureCanvas(fig)

        ax = fig.add_subplot(111)

        # Яркие цвета для разных типов
        colors = ['#70a1ff', '#7bed9f', '#ff6b81', '#ffa502', '#a4b0be']
        bars = ax.bar(types, counts, color=colors[:len(types)], edgecolor='#2f3542', linewidth=1.2)

        ax.set_xlabel('Тип аниме', fontsize=10, fontweight='bold')
        ax.set_ylabel('Количество', fontsize=10, fontweight='bold')
        ax.set_title('Распределение по типам', fontsize=11, fontweight='bold', color='#2f3542')
        ax.set_facecolor('#f1f2f6')
        fig.patch.set_facecolor('#f1f2f6')

        # Поворачиваем подписи на оси X
        ax.set_xticklabels(types, rotation=15, fontsize=9)

        # Добавляем сетку
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

        fig.tight_layout()

        layout = QVBoxLayout(self.widget_types_chart)
        layout.addWidget(canvas)