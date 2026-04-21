# Умная книга рецептов (Python + Node.js)

Демо-проект веб-сайта **«Умная книга рецептов»**:
- **Backend:** Python (FastAPI) + PostgreSQL + Alembic
- **Frontend:** Node.js (Vite + React + Tailwind)
- **Запуск:** Docker Compose (одной командой)
- **Тесты:** pytest (backend) + vitest (frontend)
- **CI/CD:** GitHub Actions (`.github/workflows/ci.yml`)

> Важно: генерация «нейро-шагов» в этом демо сделана **эвристически** (персонализация по ограничениям/желаниям). При желании можно подключить внешний LLM (ключом через env), но по умолчанию проект не требует внешних API.

---

## 1) Быстрый старт (Docker)

```bash
docker compose up --build
```

Откройте в браузере:
- http://localhost:8080

Что запустится:
- `db` — PostgreSQL
- `backend` — FastAPI на `:8000`
- `frontend` — Vite preview на `:3000`
- `nginx` — единая точка входа на `:8080` (проксирует `/` и `/api/...`)

---

## 2) Возможности

- Регистрация / вход по email+паролю (JWT хранится в HttpOnly cookie)
- Восстановление пароля (в демо токен возвращается в ответе API)
- Список продуктов пользователя (CRUD)
- Подбор рецептов по ингредиентам + критериям:
  - «не докупать продукты»
  - тип блюда (завтрак/обед/ужин/другое)
  - максимум по времени и калориям
  - сложность
- Карточки рецептов (изображение + время + тип + КБЖУ)
- Пошаговая готовка с сохранением прогресса на сервере (CookingSession)
- Оценка и отзыв
- Избранное (можно добавить **только приготовленные** блюда)
- Личный кабинет: продукты / история / отзывы / избранное / настройки ограничений

---

## 3) Данные рецептов и картинки

- При первом запуске backend автоматически:
  1) применяет миграции Alembic
  2) **засеивает базу 500 рецептами** (50 завтрак, 100 обед, 250 ужин, 100 другое)
- Картинки хранятся в PostgreSQL в виде `bytea` (сжатый `WEBP`).

---

## 4) Локальная разработка без Docker

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL='postgresql+psycopg2://postgres:postgres@localhost:5432/smart_cookbook'
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 5) Тесты

### Backend
```bash
cd backend
export TEST_DATABASE_URL='postgresql+psycopg2://postgres:postgres@localhost:5432/smart_cookbook_test'
pytest -q
```

### Frontend
```bash
cd frontend
npm test
npm run lint
```

---

## 6) Безопасность (памятка для продакшна)

- Включите HTTPS (TLS) на уровне обратного прокси (Nginx/Caddy/Traefik).
- Установите `JWT_SECRET_KEY` в **случайное длинное** значение.
- Поставьте `AUTH_COOKIE_SECURE=true`, если сайт работает по HTTPS.
- Ограничьте `CORS_ORIGINS` нужными доменами.

---

## 7) Структура репозитория

```
smart-cookbook/
  backend/
    app/
      api/routers/...
      core/...
      models/...
      schemas/...
      services/...
      seed/...
      tests/...
    alembic/...
  frontend/
    src/...
  docker/
    nginx/default.conf
  docker-compose.yml
```
