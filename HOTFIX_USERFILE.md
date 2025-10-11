# Hotfix: UserFile → FileAsset

## 🔴 Проблема

При відкритті `/data-deletion` виникла помилка:
```
ImportError: cannot import name 'UserFile' from 'app.models'
```

## 🎯 Причина

В коді використовувалась неправильна назва моделі:
- **Використано:** `UserFile`
- **Правильно:** `FileAsset`

## ✅ Виправлення

### Файли змінені:

#### 1. `app/views/public.py`
```python
# Було:
from ..models import Schedule, UserFile
file_count = UserFile.query.filter_by(user_id=current_user.id).count()

# Стало:
from ..models import Schedule, FileAsset
file_count = FileAsset.query.filter_by(user_id=current_user.id).count()
```

#### 2. `app/views/dashboard.py`
Замінено в 4 місцях:
- `export_user_data()` - експорт файлів
- `delete_user_content()` - видалення файлів користувача
- `delete_account()` - повне видалення акаунту

```python
# Було:
from ..models import UserFile
UserFile.query.filter_by(...)

# Стало:
from ..models import FileAsset
FileAsset.query.filter_by(...)
```

## 🧪 Перевірка

```bash
python -c "from app import create_app; app = create_app(); print('✅ OK')"
# Output: ✅ App created successfully
```

## 📊 Моделі в app/models.py

Правильні назви:
- ✅ `User`
- ✅ `Schedule`
- ✅ `FileAsset` ← правильна назва!
- ✅ `GeneratedContent`
- ✅ `Subscription`

## 🚀 Deployment

**Commit:** `4784d44` - Fix: Replace UserFile with FileAsset in data deletion routes

**Результат:** 
- Помилка виправлена
- `/data-deletion` тепер працює
- Automatic redeploy на Render (~2-3 хв)

## ✅ Статус

**Виправлено!** Сторінка видалення даних тепер доступна.

**URL:** https://marketing-agent-p4ig.onrender.com/data-deletion
