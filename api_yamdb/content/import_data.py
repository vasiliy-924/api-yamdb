import csv

from content.models import Category,  Genre, GenreTitle, Title
from reviews.models import Comment, Review
from users.models import User

with open('category.csv', 'r') as file:
    csvreader = csv.reader(file)
    next(csvreader)
    for row in csvreader:
        name, slug, description = row
        category = Category(name=name, slug=slug, description=description)
        category.save()
