import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class Database:
    def __init__(self, db_path: str = "anime_manager.db"):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Устанавливает соединение с базой данных"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.connection:
            self.connection.close()

    def init_db(self):
        """Инициализирует базу данных (создает таблицы если их нет)"""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Таблица жанров аниме
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS genres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')

            # Таблица аниме
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anime (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    studio TEXT,
                    genre_id INTEGER,
                    type TEXT CHECK(type IN ('TV Сериал', 'Фильм', 'OVA/OAD', 'ONA', 'Спешл')),
                    status TEXT CHECK(status IN ('Запланировано', 'Смотрю', 'Просмотрено', 'Отложено', 'Брошено')),
                    start_date TEXT,
                    finish_date TEXT,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 10),
                    review TEXT,
                    poster_image BLOB,
                    total_episodes INTEGER DEFAULT 0,
                    watched_episodes INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (genre_id) REFERENCES genres (id)
                )
            ''')

            # Добавляем стандартные жанры аниме
            default_genres = [
                'Сёнен', 'Сёдзё', 'Сейнен', 'Дзёсей', 'Комедия', 'Драма',
                'Романтика', 'Фэнтези', 'Научная фантастика', 'Хоррор',
                'Мистика', 'Приключения', 'Этти', 'Меха', 'Спокон',
                'Повседневность', 'Гурман', 'Исекай', 'Махо-сёдзё'
            ]

            for genre in default_genres:
                cursor.execute(
                    "INSERT OR IGNORE INTO genres (name) VALUES (?)",
                    (genre,)
                )

            conn.commit()

    def add_anime(self, anime_data: Dict[str, Any]) -> int:
        """Добавляет новое аниме в базу данных"""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Получаем ID жанра по имени
            genre_id = None
            if anime_data.get('genre'):
                cursor.execute("SELECT id FROM genres WHERE name = ?", (anime_data['genre'],))
                result = cursor.fetchone()
                if result:
                    genre_id = result['id']

            # Вставляем аниме
            cursor.execute('''
                INSERT INTO anime 
                (title, studio, genre_id, type, status, start_date, finish_date, 
                 rating, review, poster_image, total_episodes, watched_episodes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                anime_data['title'],
                anime_data.get('studio', ''),
                genre_id,
                anime_data.get('type', 'TV Сериал'),
                anime_data['status'],
                anime_data['start_date'],
                anime_data['finish_date'],
                anime_data['rating'],
                anime_data['review'],
                anime_data.get('poster_image'),
                anime_data.get('total_episodes', 0),
                anime_data.get('watched_episodes', 0)
            ))

            anime_id = cursor.lastrowid
            conn.commit()
            return anime_id

    def update_anime(self, anime_id: int, anime_data: Dict[str, Any]) -> bool:
        """Обновляет данные аниме"""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Получаем ID жанра по имени
            genre_id = None
            if anime_data.get('genre'):
                cursor.execute("SELECT id FROM genres WHERE name = ?", (anime_data['genre'],))
                result = cursor.fetchone()
                if result:
                    genre_id = result['id']

            cursor.execute('''
                UPDATE anime 
                SET title = ?, studio = ?, genre_id = ?, type = ?, status = ?, 
                    start_date = ?, finish_date = ?, rating = ?, review = ?,
                    poster_image = ?, total_episodes = ?, watched_episodes = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                anime_data['title'],
                anime_data.get('studio', ''),
                genre_id,
                anime_data.get('type', 'TV Сериал'),
                anime_data['status'],
                anime_data['start_date'],
                anime_data['finish_date'],
                anime_data['rating'],
                anime_data['review'],
                anime_data.get('poster_image'),
                anime_data.get('total_episodes', 0),
                anime_data.get('watched_episodes', 0),
                anime_id
            ))

            conn.commit()
            return cursor.rowcount > 0

    def delete_anime(self, anime_id: int) -> bool:
        """Удаляет аниме из базы данных"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM anime WHERE id = ?", (anime_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_anime(self, anime_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию об аниме по ID"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, g.name as genre_name 
                FROM anime a
                LEFT JOIN genres g ON a.genre_id = g.id
                WHERE a.id = ?
            ''', (anime_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_anime(self, search_text: str = "") -> List[Dict[str, Any]]:
        """Получает список всех аниме с возможностью поиска"""
        with self.connect() as conn:
            cursor = conn.cursor()

            if search_text:
                search_pattern = f"%{search_text}%"
                cursor.execute('''
                    SELECT a.*, g.name as genre_name 
                    FROM anime a
                    LEFT JOIN genres g ON a.genre_id = g.id
                    WHERE a.title LIKE ? OR a.studio LIKE ?
                    ORDER BY a.created_at DESC
                ''', (search_pattern, search_pattern))
            else:
                cursor.execute('''
                    SELECT a.*, g.name as genre_name 
                    FROM anime a
                    LEFT JOIN genres g ON a.genre_id = g.id
                    ORDER BY a.created_at DESC
                ''')

            return [dict(row) for row in cursor.fetchall()]

    def get_all_genres(self) -> List[Dict[str, Any]]:
        """Получает список всех жанров"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM genres ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Получает статистику по аниме"""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Общая статистика
            cursor.execute("SELECT COUNT(*) as total FROM anime")
            total = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as watched_count FROM anime WHERE status = 'Просмотрено'")
            watched_count = cursor.fetchone()['watched_count']

            cursor.execute("SELECT COUNT(*) as watching_count FROM anime WHERE status = 'Смотрю'")
            watching_count = cursor.fetchone()['watching_count']

            cursor.execute("SELECT COUNT(*) as planned_count FROM anime WHERE status = 'Запланировано'")
            planned_count = cursor.fetchone()['planned_count']

            cursor.execute("SELECT COUNT(*) as dropped_count FROM anime WHERE status = 'Брошено'")
            dropped_count = cursor.fetchone()['dropped_count']

            cursor.execute("SELECT AVG(rating) as avg_rating FROM anime WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()['avg_rating'] or 0

            cursor.execute("SELECT SUM(total_episodes) as total_episodes FROM anime WHERE total_episodes > 0")
            total_episodes = cursor.fetchone()['total_episodes'] or 0

            cursor.execute("SELECT SUM(watched_episodes) as watched_episodes FROM anime WHERE watched_episodes > 0")
            watched_episodes = cursor.fetchone()['watched_episodes'] or 0

            # Статистика по жанрам
            cursor.execute('''
                SELECT g.name as genre, COUNT(a.id) as count
                FROM genres g
                LEFT JOIN anime a ON g.id = a.genre_id
                GROUP BY g.name
                HAVING COUNT(a.id) > 0
                ORDER BY count DESC
            ''')
            genres_stats = [dict(row) for row in cursor.fetchall()]

            # Статистика по оценкам
            cursor.execute('''
                SELECT rating, COUNT(*) as count
                FROM anime
                WHERE rating IS NOT NULL
                GROUP BY rating
                ORDER BY rating
            ''')
            ratings_stats = [dict(row) for row in cursor.fetchall()]

            # Статистика по типам
            cursor.execute('''
                SELECT type, COUNT(*) as count
                FROM anime
                WHERE type IS NOT NULL
                GROUP BY type
                ORDER BY count DESC
            ''')
            types_stats = [dict(row) for row in cursor.fetchall()]

            # Аниме по годам (для статистики "в этом году")
            cursor.execute('''
                SELECT strftime('%Y', finish_date) as year, COUNT(*) as count
                FROM anime
                WHERE finish_date IS NOT NULL
                GROUP BY strftime('%Y', finish_date)
                ORDER BY year
            ''')
            yearly_stats = [dict(row) for row in cursor.fetchall()]

            return {
                'total': total,
                'watched_count': watched_count,
                'watching_count': watching_count,
                'planned_count': planned_count,
                'dropped_count': dropped_count,
                'avg_rating': round(avg_rating, 2) if avg_rating else 0,
                'total_episodes': total_episodes,
                'watched_episodes': watched_episodes,
                'genres_stats': genres_stats,
                'ratings_stats': ratings_stats,
                'types_stats': types_stats,
                'monthly_stats': monthly_stats,
                'yearly_stats': yearly_stats  # Добавлено
            }

    def export_to_csv(self, file_path: str) -> bool:
        """Экспортирует данные в CSV файл"""
        try:
            import csv
            anime_list = self.get_all_anime()

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'title', 'studio', 'genre', 'type', 'status',
                              'start_date', 'finish_date', 'rating', 'total_episodes',
                              'watched_episodes', 'review']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for anime in anime_list:
                    writer.writerow({
                        'id': anime['id'],
                        'title': anime['title'],
                        'studio': anime['studio'] or '',
                        'genre': anime.get('genre_name', ''),
                        'type': anime['type'],
                        'status': anime['status'],
                        'start_date': anime['start_date'],
                        'finish_date': anime['finish_date'],
                        'rating': anime['rating'] or '',
                        'total_episodes': anime['total_episodes'] or 0,
                        'watched_episodes': anime['watched_episodes'] or 0,
                        'review': anime['review'] or ''
                    })

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False