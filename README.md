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
├── docker-compose.yml          # Оркестрация сервисов (БД, кеш)
├── README.md                   # Документация проекта
├── requirements.txt            # Список зависимостей Python
├── main.py                     # Точка входа FastAPI приложения, обработка ошибок 
├── conftest.py                 # Настройки тестовой БД
|── config.py                   # я хз что конфиг у меня делает
├── db.py                       # Настройки подключения к БД
│── models.py                   # ORM-модели  
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
│   |── comment_service.py      # Бизнесс логика комментариев             
│   │── project_service.py      # Бизнесс логика проектов   
│   │── task_service.py         # Бизнесс логика задач
|   |── user_service.py         # Бизнесс логика пользователей 
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
│── cache/                 # Логика кеширования 
|   ├── comment_cache.py
|   ├── project_cache.py
│   ├── task_cache.py           
|   ├── user_cache.py
│
|
|
├── auth/                       # Аутентификация 
│   ├── security.py     # Хэширование паролей, создание текущего айди, подписание токена  
|
|
|
└── tests/                      # Тесты приложения
    ├── test_comment.py
    ├── test_project.py
    ├── test_task.py
    ├── test_user.py
```

## Установка и запуск

1. Клонируй репозиторий git clone https://github.com/Kidd-ux/task_manager