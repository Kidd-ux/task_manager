# Training Task Manager 

Training Task Manager - Это тренировочный диспетчер задач, написанный на языке Python для обучения с использованием FastAPI, SQLAlchemy, Postgres, Redis

## Возможности 

 - Добавление, управление и редактирование пользователей, проектов, задач и комментариев
 - Авторизация пользователей 
 - Аутентификация через JWT
 - Использование кеша через Redis
 - Тесты при помощи Pytest

 ## Технологический стек

- **Язык:** Python 3.11.9
- **Фреймворк:** FastAPI
- **Асинхронность:** asyncio
- **База данных:** PostgreSQL (через SQLAlchemy ORM)
- **Миграции базы данных:** Alembic
- **Схемы данных и валидация:** Pydantic v2
- **Аутентификация:** HTTPBearer, JWT
- **Хеширование паролей:** Pwdlib + Argon2
- **Кеширование** Redis
- **Тестирование:** Pytest
- **Документация:** OpenAPI (автоматически через Swagger UI)

```
task_manager/
├── Dockerfile                  # Конфигурация Docker для контейнеризации приложения
├── docker-compose.yml          # Приложение, бд, кеш
├── README.md                   # Документация проекта
├── requirements.txt            # Список зависимостей Python
├── main.py                     # Точка входа FastAPI приложения, обработка ошибок 
├── conftest.py                 # Настройки фикстур и тестов
├── config.py                   # Чтение настроек (.env)
├── db.py                       # Настройки подключения к БД
├── models.py                   # ORM-модели  
|
|
├── alembic/                    # Миграции базы данных
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Файлы версий миграций
│
├── services/                  # Основной пакет приложения
|   |
│   │
│   ├── auth_service.py         # Бизнесс логика аутентификицаии 
│   ├── comment_service.py      # Бизнесс логика комментариев             
│   ├── project_service.py      # Бизнесс логика проектов   
│   ├── task_service.py         # Бизнесс логика задач
|   └── user_service.py         # Бизнесс логика пользователей 
│    
│         
│   
|
|
├── routers/               # Эндпоинты, маршруты 
│    ├── auth.py
│    ├── comments.py
│    ├── projects.py
│    ├── tasks.py
│    └── users.py
│   
├── schemas/               # Схемы Pydantic 
│   ├── auth.py
│   ├── comment.py
│   ├── project.py
│   ├── task.py
│   └── user.py
│  
|
├── cache/                 # Логика кеширования 
|   ├── comment_cache.py
|   ├── project_cache.py
│   ├── task_cache.py           
|   └── user_cache.py
│
|
|
├── auth/                       # Аутентификация 
│   └── security.py     # Хэширование паролей, создание текущего айди, подписание токена  
|
|
|
└── tests/                      # Тесты приложения
    ├── test_comment.py
    ├── test_project.py
    ├── test_task.py
    └── test_user.py
```

## Требования

- Docker и Docker Compose (для запуска приложения)
- Python 3.11, Postgres и Redis на компьютере (только для запуска тестов)

## Запуск через Docker

1. Клонировать репозиторий и перейти в папку проекта:

   ```bash
   git clone https://github.com/Kidd-ux/task_manager
   cd task_manager
   ```

2. Создать `.env` из шаблона:

   ```bash
   # Linux / macOS
   cp .env.example .env
   # Windows
   copy .env.example .env
   ```

3. Заполнить `.env`:
   - `POSTGRES_PASSWORD` — придумать пароль. Для запуска тестов тот же пароль нужен в `DATABASE_URL` и `TEST_DATABASE_URL`.
   - `SECRET_KEY` — подпись JWT-токенов, нужна случайная строка не короче 32 байт:

     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

4. Запустить контейнеры (приложение, PostgreSQL, Redis):

   ```bash
   docker compose up --build -d
   ```

5. Применить миграции (таблицы сами не создаются). Если база ещё не успела подняться и команда вернула ошибку подключения, повторить через несколько секунд:

   ```bash
   docker compose exec fastapi alembic upgrade head
   ```

6. Документация API (Swagger): <http://localhost:8000/docs>

Остановить: `docker compose down` (данные базы сохраняются в томе `postgres_data`; `docker compose down -v` удаляет и их).

## Использование API

1. Создать пользователя: `POST /users`.
2. Получить токен: `POST /auth/login` (email и пароль).
3. В Swagger нажать **Authorize** и вставить токен. Запросы на создание, изменение и удаление требуют токен; чтение открыто всем.

## Запуск тестов

Тесты вызывают API и работают с настоящими PostgreSQL и Redis. Перед каждым тестом тестовая база и Redis очищаются.

1. Установить зависимости: `pip install -r requirements.txt`
2. Запустить PostgreSQL и Redis на адресах из `.env`.
3. Создать пустую базу `task_manager_test`. Имя обязано заканчиваться на `_test`, иначе тесты не запустятся: так защищена рабочая база.
4. Указать её в `TEST_DATABASE_URL` в `.env`.
5. Создать в ней таблицы: выполнить `alembic upgrade head`, предварительно задав в этом терминале `DATABASE_URL` равным адресу тестовой базы.

   ```bash
   # Linux / macOS
   export DATABASE_URL="<адрес тестовой базы>"
   # Windows PowerShell
   $env:DATABASE_URL="<адрес тестовой базы>"

   alembic upgrade head
   ```

6. Запустить тесты:

   ```bash
   python -m pytest tests
   ```
