# 🚀 Быстрый гайд по деплою на Render.com

## ✅ Что уже готово:

1. **Код загружен в GitHub**: https://github.com/pilipandr770/marketing-agent
2. **PostgreSQL база данных** на Render готова
3. **Все конфигурационные файлы** созданы:
   - `build.sh` - установка зависимостей и миграции
   - `Procfile` - команда запуска
   - `requirements.txt` - с psycopg2 и gunicorn
   - `runtime.txt` - Python 3.10
   - `render.yaml` - автоконфигурация

## 📋 Шаги для деплоя:

### 1. Зайдите на Render.com
- Откройте https://render.com
- Войдите через GitHub

### 2. Создайте Web Service
1. Нажмите **"New +"** → **"Web Service"**
2. Выберите репозиторий **pilipandr770/marketing-agent**
3. Настройки:
   ```
   Name: marketing-agent
   Environment: Python 3
   Build Command: ./build.sh
   Start Command: gunicorn run:app
   Plan: Free (или платный)
   ```

### 3. Добавьте переменные окружения

**Откройте файл `render-env-variables.txt`** на вашем компьютере.

В Render Dashboard → **Environment** → **Add Environment Variable**

Скопируйте и вставьте каждую переменную:

**Минимальный набор для запуска:**
```
FLASK_APP=run.py
FLASK_SECRET_KEY=<замените на случайную строку минимум 32 символа>
SQLALCHEMY_DATABASE_URI=postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
SCHEDULER_TIMEZONE=Europe/Berlin
```

**Для полного функционала добавьте все из `render-env-variables.txt`**

### 4. Запустите деплой
1. Нажмите **"Create Web Service"**
2. Дождитесь завершения (3-5 минут)
3. Render автоматически:
   - Склонирует репозиторий
   - Установит зависимости
   - **Выполнит миграции БД на PostgreSQL** ✅
   - Запустит приложение

### 5. Готово! 🎉

Ваше приложение будет доступно по адресу:
```
https://marketing-agent.onrender.com
```
(или с вашим custom именем)

## 🔍 Проверка миграций

После деплоя проверьте логи:
1. Render Dashboard → **Logs**
2. Найдите строки:
   ```
   Running migrations...
   INFO [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO [alembic.runtime.migration] Will assume transactional DDL.
   ```

Это значит миграции успешно выполнены! ✅

## 📊 База данных

Ваша PostgreSQL база будет содержать таблицы:
- `user` - пользователи
- `schedule` - расписания
- `file_asset` - загруженные файлы
- `generated_content` - сгенерированный контент

## ⚙️ Что происходит при деплое:

```bash
# build.sh выполняет:
1. pip install -r requirements.txt  # Установка всех зависимостей
2. flask db upgrade                 # Миграции на PostgreSQL ✅
```

## 🔄 Автоматические обновления

При каждом `git push origin main`:
- Render автоматически запустит новый деплой
- Выполнит миграции если есть изменения в models.py
- Перезапустит приложение

## ⚠️ Важно знать:

### Free Plan:
- ✅ Бесплатно для тестирования
- ⏱️ Приложение "засыпает" через 15 минут неактивности
- 🐌 Первый запрос после пробуждения ~30 сек
- 🔄 Для production используйте платный план ($7/мес)

### Custom Domain:
Можете добавить свой домен в Render Dashboard → Settings → Custom Domain

## 🆘 Troubleshooting

### Если что-то не работает:

1. **Проверьте логи**: Dashboard → Logs
2. **Миграции не выполнились?**
   - Зайдите в Shell (Dashboard → Shell)
   - Выполните вручную: `flask db upgrade`
3. **Приложение не запускается?**
   - Проверьте все Environment Variables
   - Убедитесь что SQLALCHEMY_DATABASE_URI правильный

## 📧 Поддержка

Если нужна помощь:
- Документация Render: https://render.com/docs
- Логи в Dashboard покажут точную ошибку

---

**Готово к деплою! Удачи! 🚀**
