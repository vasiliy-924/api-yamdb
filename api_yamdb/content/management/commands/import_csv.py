import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from content.models import Category, Genre, Title
from reviews.models import Comment, Review
from users.models import User

TitleGenre = Title.genre.through


class Command(BaseCommand):
    help = (
        'Импортирует данные из csv-файлов в static/data/ в базу данных, '
        'включая m2m Title-Genre'
    )

    def handle(self, *args, **options):
        model_file_map = {
            User: 'users.csv',
            Category: 'category.csv',
            Genre: 'genre.csv',
            Title: 'titles.csv',
            Review: 'review.csv',
            Comment: 'comments.csv',
            TitleGenre: 'genre_title.csv',
        }

        related_fields = {
            Review: {'author': User, 'title': Title},
            Comment: {'author': User, 'review': Review},
            Title: {'category': Category},
        }

        csv_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        try:
            for model, filename in model_file_map.items():
                file_path = os.path.join(csv_dir, filename)
                instances = []
                with open(file_path, encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        fields = {}
                        if model is TitleGenre:
                            title = Title.objects.get(id=row['title_id'])
                            genre = Genre.objects.get(id=row['genre_id'])
                            instances.append(
                                TitleGenre(title=title, genre=genre)
                            )
                            continue
                        for field_name, value in row.items():
                            if (
                                model in related_fields
                                and field_name in related_fields[model]
                            ):
                                rel_model = related_fields[model][field_name]
                                fields[field_name] = (
                                    rel_model.objects.get(id=value)
                                    if value else None
                                )
                            else:
                                fields[field_name] = value
                        instances.append(model(**fields))
                model.objects.bulk_create(instances, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                'Импорт данных завершён успешно!'))
        except Exception as e:
            raise CommandError(f'Ошибка при импорте: {e}')
