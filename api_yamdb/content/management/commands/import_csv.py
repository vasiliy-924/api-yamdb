import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from content.models import Category, Genre, Title
from reviews.models import Review, Comment
from users.models import User


CSV_DIR = os.path.join(settings.BASE_DIR, 'static', 'data')


class Command(BaseCommand):
    """Команда для импорта данных из csv-файлов в базу данных."""
    help = 'Импортирует данные из csv-файлов в static/data/ в базу данных'

    def handle(self, *args, **options):
        """Запускает импорт всех сущностей из csv-файлов."""
        try:
            self.import_users()
            self.import_categories()
            self.import_genres()
            self.import_titles()
            self.import_genre_title()
            self.import_reviews()
            self.import_comments()
            self.stdout.write(self.style.SUCCESS(
                'Импорт данных завершён успешно!'))
        except Exception as e:
            raise CommandError(f'Ошибка при импорте: {e}')

    def import_users(self):
        """Импортирует пользователей из users.csv."""
        path = os.path.join(CSV_DIR, 'users.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    User.objects.get_or_create(
                        id=row['id'],
                        username=row['username'],
                        email=row['email'],
                        role=row.get('role', 'user'),
                        bio=row.get('bio', ''),
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                    )
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в users.csv, строка {row}: {e}')

    def import_categories(self):
        """Импортирует категории из category.csv."""
        path = os.path.join(CSV_DIR, 'category.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    Category.objects.get_or_create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug'],
                    )
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в category.csv, строка {row}: {e}')

    def import_genres(self):
        """Импортирует жанры из genre.csv."""
        path = os.path.join(CSV_DIR, 'genre.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    Genre.objects.get_or_create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug'],
                    )
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в genre.csv, строка {row}: {e}')

    def import_titles(self):
        """Импортирует произведения из titles.csv."""
        path = os.path.join(CSV_DIR, 'titles.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    category = None
                    if row['category']:
                        category = Category.objects.get(id=row['category'])
                    Title.objects.get_or_create(
                        id=row['id'],
                        name=row['name'],
                        year=row['year'],
                        category=category,
                    )
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в titles.csv, строка {row}: {e}')

    def import_genre_title(self):
        """Импортирует связи жанров и произведений из genre_title.csv."""
        path = os.path.join(CSV_DIR, 'genre_title.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в genre_title.csv, строка {row}: {e}')

    def import_reviews(self):
        """Импортирует отзывы из review.csv."""
        path = os.path.join(CSV_DIR, 'review.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    author = User.objects.get(id=row['author'])
                    title = Title.objects.get(id=row['title_id'])
                    Review.objects.get_or_create(
                        id=row['id'],
                        title=title,
                        text=row['text'],
                        author=author,
                        score=row['score'],
                        pub_date=row['pub_date'],
                    )
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в review.csv, строка {row}: {e}')

    def import_comments(self):
        """Импортирует комментарии из comments.csv."""
        path = os.path.join(CSV_DIR, 'comments.csv')
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    author = User.objects.get(id=row['author'])
                    review = Review.objects.get(id=row['review_id'])
                    Comment.objects.get_or_create(
                        id=row['id'],
                        review=review,
                        text=row['text'],
                        author=author,
                        pub_date=row['pub_date'],
                    )
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в comments.csv, строка {row}: {e}')
