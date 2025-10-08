# ⚡ Быстрая инструкция - Render Shell

## Что изменилось
✅ Добавлена поддержка схемы `marketing_agent` во всех моделях
✅ Новая миграция создает отдельную схему для изоляции от других проектов
✅ Код запушен на GitHub, Render автоматически задеплоит

## 🚀 Выполните в Render Shell (5 минут):

### 1. Откройте Shell
https://dashboard.render.com/ → marketing-agent → Shell

### 2. Удалите старую историю миграций
```bash
flask shell
```

```python
from sqlalchemy import text
from app import db
with db.engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    conn.commit()
exit()
```

### 3. Создайте схему
```bash
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

### 4. Примените миграции
```bash
flask db stamp head
flask db upgrade
```

### 5. Готово! 🎉
Закройте Shell, подождите перезапуска сервиса (1 минута).
Проверьте: https://marketing-agent-p4ig.onrender.com/dashboard/

---

## Что это дает?
✅ Таблицы в схеме `marketing_agent`, не трогают `public`
✅ Другие проекты в базе остаются нетронутыми
✅ Полная изоляция данных
✅ Нет конфликтов имен таблиц

Подробные инструкции: **SCHEMA-SETUP-INSTRUCTIONS.md**
