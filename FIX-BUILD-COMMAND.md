# 🚨 КРИТИЧНО: Настройка Build Command в Render

## Проблема
Render пытается применить старую миграцию `24cd1a550277`, которой больше нет в коде.

## ✅ Решение (2 минуты)

### Шаг 1: Настройте Build Command

1. Откройте **Render Dashboard**: https://dashboard.render.com/
2. Выберите сервис **marketing-agent**
3. Перейдите в **Settings** (левое меню)
4. Найдите секцию **Build & Deploy**
5. В поле **Build Command** вставьте:

```bash
./build.sh
```

ИЛИ (если не работает):

```bash
pip install -r requirements.txt && flask db stamp head && flask db upgrade
```

6. Нажмите **Save Changes**

### Шаг 2: Очистите кэш и задеплойте

1. Нажмите **Manual Deploy** (вверху справа)
2. Выберите **Clear build cache & deploy**
3. Подождите 2-3 минуты

### Ожидаемый результат:

```
🔧 Installing dependencies...
Successfully installed Flask-3.0.3 ...

🔄 Resetting migration history...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.

🚀 Applying database migrations...
INFO  [alembic.runtime.migration] Running upgrade  -> marketing_agent_schema

✅ Build completed successfully!
```

---

## Если всё равно ошибка:

### План Б: Используйте Render Shell

```bash
# 1. Откройте Shell в Render Dashboard
# 2. Выполните:

flask shell
```

```python
from sqlalchemy import text
from app import db

# Удаляем старую историю миграций
with db.engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    conn.commit()

exit()
```

```bash
# 3. Создайте схему
flask shell
```

```python
from sqlalchemy import text
from app import db

with db.engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS marketing_agent"))
    conn.commit()

exit()
```

```bash
# 4. Примените миграции
flask db stamp head
flask db upgrade
```

Закройте Shell, сервис перезапустится автоматически.

---

## После успешного деплоя:

✅ Проверьте: https://marketing-agent-p4ig.onrender.com/
✅ Зарегистрируйте нового пользователя
✅ Проверьте Dashboard

🎉 **Готово!** Все таблицы теперь в схеме `marketing_agent`!
