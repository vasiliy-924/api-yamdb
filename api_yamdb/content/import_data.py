import csv

from content.models import Category, Genre, TitleGenre, Title
from reviews.models import Comment, Review
from users.models import User

TABLES = {
    Category: 'category.csv',
    Comment: 'comments.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    TitleGenre: 'genre_title.csv',
    Review: 'review.csv',
    User: 'users.csv',
}

for model, filename in TABLES.items():
    with open(filename, 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for row in csvreader:
            if model == Category:
                name, slug, description = row
                instance = model(name=name, slug=slug, description=description)
            elif model == Comment:
                review_id, text, author, pub_date = row
                instance = model(
                    text=text,
                    author_id=author,
                    review_id=review_id,
                    pub_date=pub_date
                )
            elif model == Genre:
                name, slug = row
                instance = model(name=name, slug=slug)
            elif model == TitleGenre:
                title_id, genre_id = row
                instance = model(title_id=title_id, genre_id=genre_id)
            elif model == Review:
                title_id, text, author, score, pub_date = row
                instance = model(
                    title_id=title_id,
                    text=text,
                    author=author,
                    score=score,
                    pub_date=pub_date
                )
            elif model == Title:
                name, year, category = row
                instance = model(name=name, year=year, category=category)
            elif model == User:
                username, email, role, bio, first_name, last_name = row
                instance = model(
                    username=username,
                    email=email,
                    role=role,
                    bio=bio,
                    first_name=first_name,
                    last_name=last_name
                )
            instance.save()
