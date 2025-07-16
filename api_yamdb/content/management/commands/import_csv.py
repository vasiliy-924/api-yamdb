import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from content.models import Category, Genre, Title
from reviews.models import Comment, Review
from users.models import User


class Command(BaseCommand):
    help = 'Импортирует данные из csv-файлов в static/data/ в базу данных'

    def handle(self, *args, **options):
        MODEL_FILE_MAP = {
            User: 'users.csv',
            Category: 'category.csv',
            Genre: 'genre.csv',
            Title: 'titles.csv',
            Review: 'review.csv',
            Comment: 'comments.csv',
        }

        RELATED_FIELDS = {
            Review: {'author': User, 'title': Title},
            Comment: {'author': User, 'review': Review},
            Title: {'category': Category},
        }

        csv_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        try:
            for model, filename in MODEL_FILE_MAP.items():
                file_path = os.path.join(csv_dir, filename)
                instances = []
                with open(file_path, encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        fields = {}
                        for field_name, value in row.items():
                            if model in RELATED_FIELDS and field_name in RELATED_FIELDS[model]:
                                rel_model = RELATED_FIELDS[model][field_name]
                                fields[field_name] = rel_model.objects.get(id=value) if value else None
                            else:
                                fields[field_name] = value
                        instances.append(model(**fields))
                model.objects.bulk_create(instances, ignore_conflicts=True)

            # обработка связей "title-genre"
            genre_title_path = os.path.join(csv_dir, 'genre_title.csv')
            with open(genre_title_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)

            self.stdout.write(self.style.SUCCESS('Импорт данных завершён успешно!'))
        except Exception as e:
            raise CommandError(f'Ошибка при импорте: {e}')
