# YaMDb API

## Описание

**YaMDb** — сервис для сбора отзывов пользователей на различные произведения искусства: книги, фильмы, музыку и др. Сами произведения не хранятся, только информация о них, отзывы, оценки и комментарии пользователей.

- Произведения делятся на категории (например, «Книги», «Фильмы», «Музыка»).
- Каждое произведение может иметь один или несколько жанров.
- Пользователи могут оставлять отзывы и оценки (от 1 до 10), а также комментировать отзывы других пользователей.
- Из оценок формируется усреднённый рейтинг произведения.

## Алгоритм регистрации пользователей

1. Пользователь отправляет POST-запрос с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
2. Сервис YaMDb отправляет письмо с кодом подтверждения (`confirmation_code`) на указанный email.
3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/` и получает JWT-токен.
4. После регистрации и получения токена пользователь может отправить PATCH-запрос на `/api/v1/users/me/` и заполнить профиль.

## Пользовательские роли

- **Аноним** — может просматривать описания произведений, отзывы и комментарии.
- **Аутентифицированный пользователь** (`user`) — может публиковать отзывы, ставить оценки, комментировать, редактировать и удалять свои отзывы и комментарии.
- **Модератор** (`moderator`) — может удалять и редактировать любые отзывы и комментарии.
- **Администратор** (`admin`) — полные права на управление контентом и пользователями.
- **Суперпользователь Django** — всегда обладает правами администратора.

## Структура и ресурсы API

Все запросы к API начинаются с `/api/v1/`.

- **AUTH** — регистрация и получение токенов
- **USERS** — управление пользователями
- **CATEGORIES** — категории произведений
- **GENRES** — жанры произведений
- **TITLES** — произведения
- **REVIEWS** — отзывы на произведения
- **COMMENTS** — комментарии к отзывам

## Описание эндпоинтов

### AUTH
- `POST /auth/signup/` — регистрация нового пользователя (email, username)
- `POST /auth/token/` — получение JWT-токена (username, confirmation_code)

### USERS
- `GET /users/` — список пользователей (админ)
- `POST /users/` — добавить пользователя (админ)
- `GET /users/{username}/` — получить пользователя (админ)
- `PATCH /users/{username}/` — изменить пользователя (админ)
- `DELETE /users/{username}/` — удалить пользователя (админ)
- `GET /users/me/` — получить свой профиль (авторизованный пользователь)
- `PATCH /users/me/` — изменить свой профиль (авторизованный пользователь)

### CATEGORIES
- `GET /categories/` — список категорий
- `POST /categories/` — добавить категорию (админ)
- `DELETE /categories/{slug}/` — удалить категорию (админ)

### GENRES
- `GET /genres/` — список жанров
- `POST /genres/` — добавить жанр (админ)
- `DELETE /genres/{slug}/` — удалить жанр (админ)

### TITLES
- `GET /titles/` — список произведений (фильтрация по категории, жанру, названию, году)
- `POST /titles/` — добавить произведение (админ)
- `GET /titles/{title_id}/` — получить произведение
- `PATCH /titles/{title_id}/` — изменить произведение (админ)
- `DELETE /titles/{title_id}/` — удалить произведение (админ)

### REVIEWS
- `GET /titles/{title_id}/reviews/` — список отзывов к произведению
- `POST /titles/{title_id}/reviews/` — добавить отзыв (один отзыв на произведение от пользователя)
- `GET /titles/{title_id}/reviews/{review_id}/` — получить отзыв
- `PATCH /titles/{title_id}/reviews/{review_id}/` — изменить отзыв (автор, модератор, админ)
- `DELETE /titles/{title_id}/reviews/{review_id}/` — удалить отзыв (автор, модератор, админ)

### COMMENTS
- `GET /titles/{title_id}/reviews/{review_id}/comments/` — список комментариев к отзыву
- `POST /titles/{title_id}/reviews/{review_id}/comments/` — добавить комментарий (авторизованный пользователь)
- `GET /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — получить комментарий
- `PATCH /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — изменить комментарий (автор, модератор, админ)
- `DELETE /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` — удалить комментарий (автор, модератор, админ)

## Описание моделей (schemas)

### User
- `username` (строка, уникальное, ≤150 символов)
- `email` (строка, email, уникальное)
- `first_name`, `last_name` (строка, ≤150)
- `bio` (строка)
- `role` (user/moderator/admin)

### Title
- `id` (int)
- `name` (строка)
- `year` (int)
- `rating` (int, средний рейтинг)
- `description` (строка)
- `genre` (список жанров)
- `category` (категория)

### Genre
- `name` (строка)
- `slug` (строка, уникальное)

### Category
- `name` (строка)
- `slug` (строка, уникальное)

### Review
- `id` (int)
- `text` (строка)
- `author` (username)
- `score` (int, 1-10)
- `pub_date` (datetime)

### Comment
- `id` (int)
- `text` (строка)
- `author` (username)
- `pub_date` (datetime)

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:vasiliy-924/api-yamdb.git
   cd api_yamdb
   ```
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Выполните миграции и создайте суперпользователя:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```

## Импорт данных

В директории `api_yamdb/static/data/` находятся csv-файлы для наполнения базы данных. После создания моделей используйте команду для импорта данных (см. документацию проекта).
```bash
python manage.py import csv
```

## Тестирование

```bash
pytest
```

## Документация

Документация доступна по адресу: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

## Авторство

**Василий Петров (Тимлид)** - [GitHub https://github.com/vasiliy-924](https://github.com/vasiliy-924)

**Дмитрий Трегубов** - [GitHub https://github.com/DmitryTre](https://github.com/DmitryTre)

**Кирилл Домников** - [GitHub https://github.com/KirD-1](https://github.com/KirD-1)