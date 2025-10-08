# Исправление миграций в Render Shell

## Проблема
База данных содержит ссылку на миграцию `add_image_data_field`, которой нет в коде.

## Решение - Выполните в Render Shell:

### Вариант 1: Через Flask Shell (РЕКОМЕНДУЕТСЯ)

```bash
flask shell
```

В открывшемся Python shell:
```python
from sqlalchemy import text
from app import db

# Удаляем историю миграций
with db.engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    conn.commit()

exit()
```

Затем:
```bash
flask db stamp head
flask db upgrade
```

---

### Вариант 2: Прямой SQL (если Flask shell не работает)

```bash
# Подключитесь к базе данных напрямую
psql $DATABASE_URL

# В psql выполните:
DROP TABLE IF EXISTS alembic_version CASCADE;
\q

# Затем примените миграции:
flask db stamp head
flask db upgrade
```

---

### Вариант 3: Удаление всех таблиц и пересоздание

⚠️ **ВНИМАНИЕ: Это удалит ВСЕ данные (включая зарегистрированных пользователей)!**

```bash
flask shell
```

```python
from app import db
db.drop_all()
db.create_all()
exit()
```

Затем:
```bash
flask db stamp head
```

---

## Что произойдет после исправления:

✅ Таблица `generated_content` получит недостающую колонку `user_id`
✅ Dashboard начнет работать
✅ Все функции станут доступны

---

## Проверка после исправления:

После выполнения команд проверьте:
1. Откройте https://marketing-agent-p4ig.onrender.com/dashboard/
2. Должна загрузиться страница Dashboard без ошибок
3. Если всё работает - готово! 🎉
