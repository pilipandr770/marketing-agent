# Деплой на Render.com

## Подготовка завершена! ✅

Все необходимые файлы для деплоя созданы:

- ✅ `requirements.txt` - обновлен с psycopg2-binary и gunicorn
- ✅ `build.sh` - скрипт для установки зависимостей и миграций
- ✅ `Procfile` - команда запуска приложения
- ✅ `runtime.txt` - версия Python
- ✅ `render.yaml` - конфигурация для автоматического деплоя
- ✅ `.env` обновлен с PostgreSQL URL

## Шаги для деплоя:

### 1. Загрузите код в GitHub (уже сделано ✅)
```bash
git add .
git commit -m "Prepare for Render.com deployment"
git push origin main
```

### 2. Создайте Web Service на Render.com

1. Зайдите на [render.com](https://render.com)
2. Нажмите **New +** → **Web Service**
3. Подключите ваш GitHub репозиторий: `pilipandr770/marketing-agent`
4. Настройте параметры:
   - **Name:** marketing-agent
   - **Environment:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn run:app`
   - **Plan:** Free (или платный для production)

### 3. Настройте переменные окружения

В разделе **Environment** добавьте следующие переменные:

#### Обязательные:
```
FLASK_SECRET_KEY=<сгенерируйте длинный случайный ключ>
SQLALCHEMY_DATABASE_URI=postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
FLASK_APP=run.py
```

#### Опциональные (OpenAI):
```
OPENAI_API_KEY=<ваш_ключ>
OPENAI_ASSISTANT_ID=<ваш_assistant_id>
OPENAI_VECTOR_STORE_ID=<ваш_vector_store_id>
```

#### Stripe (для платежей):
```
STRIPE_PUBLIC_KEY=<ваш_ключ>
STRIPE_SECRET_KEY=<ваш_ключ>
STRIPE_WEBHOOK_SECRET=<webhook_secret>
STRIPE_PRICE_BASIC=<price_id>
STRIPE_PRICE_PRO=<price_id>
STRIPE_PRICE_ENTERPRISE=<price_id>
```

#### Telegram (опционально):
```
TELEGRAM_BOT_TOKEN=<ваш_токен>
TELEGRAM_CHAT_ID=<chat_id>
```

#### Scheduler:
```
SCHEDULER_TIMEZONE=Europe/Berlin
```

### 4. Деплой

1. Нажмите **Create Web Service**
2. Render автоматически:
   - Склонирует репозиторий
   - Установит зависимости из `requirements.txt`
   - Выполнит миграции через `build.sh`
   - Запустит приложение через gunicorn
   
3. Дождитесь завершения (займет 3-5 минут)
4. Ваше приложение будет доступно по адресу: `https://marketing-agent.onrender.com`

## Важные замечания:

### База данных PostgreSQL
- ✅ URL уже добавлен в `.env`
- ✅ Миграции выполнятся автоматически при первом деплое
- ⚠️ Убедитесь, что база данных на Render активна

### Free Plan ограничения:
- Приложение "засыпает" после 15 минут неактивности
- Первый запрос после пробуждения занимает ~30 секунд
- Для production используйте платный план

### После деплоя:
1. Откройте URL вашего приложения
2. Зарегистрируйте первого пользователя
3. Настройте API ключи в settings
4. Протестируйте функционал

## Автоматические обновления

При каждом push в `main` ветку GitHub:
- Render автоматически запустит новый деплой
- Выполнит миграции если есть изменения
- Перезапустит приложение

## Мониторинг

В Render Dashboard вы можете:
- Просматривать логи приложения
- Мониторить использование ресурсов
- Настроить автоматические бэкапы БД
- Добавить custom domain

## Troubleshooting

### Если миграции не выполнились:
```bash
# В Render Shell (доступен в Dashboard):
flask db upgrade
```

### Проверить логи:
В Render Dashboard → Logs → посмотрите вывод build.sh

### Если приложение не запускается:
1. Проверьте все environment variables
2. Убедитесь что SQLALCHEMY_DATABASE_URI правильный
3. Проверьте логи на наличие ошибок

## Готово! 🚀

Теперь ваше приложение готово к деплою на Render.com!
