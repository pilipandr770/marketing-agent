# 🔧 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: SQLAlchemy + psycopg3

## ❌ Проблема:
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Причина:** 
1. Render игнорирует `runtime.txt` и использует Python 3.13.4 по умолчанию
2. SQLAlchemy по умолчанию ищет драйвер `psycopg2`
3. Но у нас установлен `psycopg` (версия 3)

## ✅ РЕШЕНИЕ:

### Нужно изменить DATABASE_URI в Render Dashboard!

В DATABASE_URI нужно явно указать драйвер `psycopg` вместо дефолтного `psycopg2`:

### ❌ Было (неправильно):
```
postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
```

### ✅ Должно быть (правильно):
```
postgresql+psycopg://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
```

**Обратите внимание:** добавлен `+psycopg` после `postgresql`!

---

## 🚀 ЧТО ДЕЛАТЬ ПРЯМО СЕЙЧАС:

### Шаг 1: Откройте Render Dashboard
1. Зайдите на https://dashboard.render.com
2. Откройте ваш сервис `marketing-agent`

### Шаг 2: Измените Environment Variable
1. Перейдите в **Environment** (слева в меню)
2. Найдите переменную `SQLALCHEMY_DATABASE_URI`
3. Нажмите **Edit** (карандаш справа)
4. Замените значение на:
   ```
   postgresql+psycopg://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
   ```
5. Нажмите **Save Changes**

### Шаг 3: Перезапустите сервис
Render автоматически перезапустит сервис с новой переменной! ✅

---

## 📝 Объяснение:

### Формат DATABASE_URI:
```
postgresql+DRIVER://user:password@host/database
          ↑
          └─ Указываем конкретный драйвер
```

### Поддерживаемые драйверы:
- `postgresql+psycopg2` → psycopg2 (старый, не работает с Python 3.13)
- `postgresql+psycopg` → psycopg3 (новый, работает с Python 3.13) ✅
- `postgresql` → по умолчанию ищет psycopg2 ❌

---

## 🔄 Альтернативное решение (если не помогло):

Если Render все равно использует Python 3.13, можно принудительно установить версию:

### В Render Dashboard → Settings:
Добавьте Build Command:
```bash
pyenv install 3.12.0 && pyenv global 3.12.0 && ./build.sh
```

Но **проще и правильнее** использовать `+psycopg` в URI!

---

## ✨ После исправления:

Вы увидите в логах:
```
==> Running 'gunicorn run:app -c gunicorn.conf.py'
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Booting worker with pid: XX
```

**Приложение запустится!** 🎉

---

## 📋 Краткая инструкция:

1. **Render Dashboard** → ваш сервис
2. **Environment** → найти `SQLALCHEMY_DATABASE_URI`
3. **Edit** → заменить `postgresql://` на `postgresql+psycopg://`
4. **Save Changes** → дождаться перезапуска

**Готово!** ✅
