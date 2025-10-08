# 🎯 Инструкции для создания схемы marketing_agent в Render Shell

## Проблема
Ваша база данных содержит много проектов, и таблицы создавались в схеме `public` вместо отдельной схемы `marketing_agent`.

## Решение

### Шаг 1: Откройте Render Shell
1. https://dashboard.render.com/
2. Ваш сервис `marketing-agent`
3. Кнопка **Shell** (справа вверху)

### Шаг 2: Удалите старую таблицу истории миграций

```bash
flask shell
```

Затем в Python shell:
```python
from sqlalchemy import text
from app import db

# Удаляем старую историю миграций
with db.engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    conn.commit()
    print("✅ История миграций удалена!")

exit()
```

### Шаг 3: Создайте схему marketing_agent

```bash
flask shell
```

```python
from sqlalchemy import text
from app import db

# Создаем новую схему для проекта
with db.engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS marketing_agent"))
    conn.commit()
    print("✅ Схема marketing_agent создана!")

exit()
```

### Шаг 4: Примените миграции

```bash
flask db stamp head
flask db upgrade
```

Вы должны увидеть:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> marketing_agent_schema
✅ Миграция применена!
```

### Шаг 5: Проверьте результат

```bash
flask shell
```

```python
from app import db
from app.models import User

# Проверяем что таблица создана в правильной схеме
result = db.session.execute(db.text("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'marketing_agent'
"""))
print("✅ Таблицы в схеме marketing_agent:")
for row in result:
    print(f"  - {row[1]}")

exit()
```

Вы должны увидеть:
```
✅ Таблицы в схеме marketing_agent:
  - user
  - schedule
  - file_asset
  - generated_content
  - alembic_version
```

### Шаг 6: Перезапустите сервис

В Render Dashboard:
- **Manual Deploy** → **Clear build cache & deploy**

Или просто подождите автоматического перезапуска после закрытия Shell.

---

## После выполнения

✅ Все таблицы будут в схеме `marketing_agent`
✅ Не будет конфликтов с другими проектами
✅ Dashboard и все функции заработают
✅ База данных останется с вашими другими проектами

---

## Если что-то пошло не так

### Проверить существующие схемы:
```sql
\dn
```

### Удалить таблицы из схемы public (если создались там):
```bash
flask shell
```

```python
from sqlalchemy import text
from app import db

with db.engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS public.generated_content CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS public.file_asset CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS public.schedule CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS public.user CASCADE"))
    conn.commit()
    print("✅ Старые таблицы из public удалены!")

exit()
```

Затем повторите Шаги 3-4.

---

## Важно! 

После применения миграций **НЕ** забудьте:
1. Зарегистрировать нового пользователя (старые в `public.user` останутся нетронутыми)
2. Проверить что Dashboard открывается без ошибок
3. Протестировать все функции

🎉 Готово! Теперь ваш проект изолирован в отдельной схеме!
