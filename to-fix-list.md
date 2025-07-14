# Список не прошедших тестов Postman

## 1. username_and_email_both_in_use_by_different_users
**Endpoint:** `POST /api/v1/auth/signup/`  
**Ожидалось:**  
- Статус-код: 400  
- Структура ответа:  
  ```json
  {
    "email": ["string"],
    "username": ["string"]
  }
  ```
**Фактически:**  
- Статус-код: 400  
- Структура ответа: не соответствует ожидаемой (детали см. в ответе сервера).

---

## 2. username_in_use
**Endpoint:** `POST /api/v1/auth/signup/`  
**Ожидалось:**  
- Статус-код: 400  
- Структура ответа:  
  ```json
  {
    "username": ["string"]
  }
  ```
**Фактически:**  
- Статус-код: 400  
- Структура ответа: не соответствует ожидаемой (детали см. в ответе сервера).

---

## 3. create_title_only_required_fields // Admin
**Endpoint:** `POST /api/v1/titles/`  
**Ожидалось:**  
- Статус-код: 201  
- Структура ответа: корректная структура Title  
**Фактически:**  
- Статус-код: 400  
- Структура ответа: не соответствует ожидаемой (ошибка валидации, возможно, требуется обязательное поле).

---

## 4. create_title_with_empty_genre // Admin
**Endpoint:** `POST /api/v1/titles/`  
**Ожидалось:**  
- Статус-код: 400  
**Фактически:**  
- Статус-код: 201  
- Сервер создал объект, хотя жанр пустой.

---

## 5. create_comment_with_wrong_ids_in_url // User
**Endpoint:** `POST /api/v1/titles/1/reviews/4/comments/`  
**Ожидалось:**  
- Статус-код: 404  
**Фактически:**  
- Статус-код: 201  
- Сервер создал комментарий по несуществующему review.

---

## 6. get_comment_with_wrong_title_id // No Auth
**Endpoint:** `GET /api/v1/titles/1/reviews/3/comments/4/`  
**Ожидалось:**  
- Статус-код: 404  
**Фактически:**  
- Статус-код: 200  
- Сервер вернул комментарий, хотя title не совпадает с review.

---

## 7. update_comment_with_wrong_title_id // Admin
**Endpoint:** `PATCH /api/v1/titles/1/reviews/3/comments/4/`  
**Ожидалось:**  
- Статус-код: 404  
**Фактически:**  
- Статус-код: 200  
- Сервер обновил комментарий, хотя title не совпадает с review.

---

## 8. delete_comment_with_wrong_title_id // Admin
**Endpoint:** `DELETE /api/v1/titles/1/reviews/3/comments/4/`  
**Ожидалось:**  
- Статус-код: 404  
**Фактически:**  
- Статус-код: 204  
- Сервер удалил комментарий, хотя title не совпадает с review.

---

## 9. delete_comment // Moderator
**Endpoint:** `DELETE /api/v1/titles/2/reviews/1/comments/4/`  
**Ожидалось:**  
- Статус-код: 204  
**Фактически:**  
- Статус-код: 404  
- Сервер не нашёл комментарий, хотя должен был удалить.

---

## 10. delete_short_title // Admin
**Endpoint:** `DELETE /api/v1/titles/{{adminShortTitle}}/`  
**Ожидалось:**  
- Статус-код: 204  
**Фактически:**  
- Статус-код: 404  
- Сервер не нашёл title, хотя должен был удалить.

---

## 11. get_comment_with_wrong_review_id // No Auth
**Endpoint:** `GET /api/v1/titles/2/reviews/1/comments/4/`  
**Ожидалось:**  
- Статус-код: 404  
**Фактически:**  
- Статус-код: 200  
- Сервер вернул комментарий, хотя review не совпадает с title.

---

> Для каждого теста проверьте логику проверки связей между title, review, comment, а также обработку ошибок и валидацию входных данных. 