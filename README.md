# Веб-приложение для создания и обмена короткими сообщениями

## Установка

### Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:heydolono/rupor.git
```
```
cd rupor/
```

### Установка зависимостей
```
cd backend/
```
```
pip install -r requirements.txt
```

### Переменные среды

```
cd ../infra/
```
```
touch .env
```
Заполните .env в соответствии с .env.example
Пример:
```
SECRET_KEY=SECRET
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Запустить Docker Compose и заполнить данные:
Локальный запуск:
```
docker compose up -d
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic --noinput
```
