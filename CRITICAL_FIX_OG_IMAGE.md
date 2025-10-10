# ⚠️ КРИТИЧНА ПОМИЛКА: Недействительный тип контента изображения

## 🔴 Проблема

Facebook Sharing Debugger показує:
```
⚠️ Недействительный тип контента изображения
URL: https://your-domain.com/static/img/og-default.jpg
```

## 🎯 Причина

На **Render.com** в Environment Variables встановлено `OG_IMAGE_ABS` з placeholder URL замість реального домену.

---

## ✅ ШВИДКЕ ВИПРАВЛЕННЯ (2 хвилини)

### Крок 1: Відкрийте Render Dashboard
🔗 https://dashboard.render.com/

### Крок 2: Виберіть сервіс
Клікніть на `marketing-agent-p4ig`

### Крок 3: Environment Variables
Ліва панель → **"Environment"**

### Крок 4: Знайдіть OG_IMAGE_ABS
Прокрутіть список змінних, знайдіть `OG_IMAGE_ABS`

### Крок 5A: ВИДАЛИТИ (РЕКОМЕНДОВАНО) ✅
1. Натисніть іконку смітника праворуч від `OG_IMAGE_ABS`
2. Підтвердіть видалення
3. **Готово!** Render автоматично redeploy (2-3 хв)

**АБО**

### Крок 5B: Змінити значення
Якщо `OG_IMAGE_ABS` = `https://your-domain.com/...`

**Змініть на:**
```
https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

Натисніть **"Save Changes"**

---

## 🧪 Перевірка після виправлення

### Чекаємо deployment (~2-3 хвилини)

Render покаже в логах:
```
==> Your service is live 🎉
```

### Тест 1: Перевірка зображення (30 сек)

Відкрийте в браузері:
```
https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

**Очікуваний результат:** Зображення 1200x630px з текстом "🤖 Marketing Agent"

❌ Якщо 404 → зображення не завантажилось, перевірте deployment logs

### Тест 2: Facebook Sharing Debugger (1 хв)

1. Відкрийте: https://developers.facebook.com/tools/debug/
2. Введіть: `https://marketing-agent-p4ig.onrender.com`
3. Натисніть **"Debug"**
4. Натисніть **"Scrape Again"** (щоб оновити кеш)

**Очікуваний результат:**
```
✅ og:image: https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
✅ Image Width: 1200px
✅ Image Height: 630px
✅ Image Type: image/jpeg
❌ Немає попереджень!
```

### Тест 3: Локальний діагностичний скрипт

```bash
python diagnose_og.py
```

Має показати:
```
✅ Everything looks good!
```

---

## 💡 Чому це працює?

### Якщо `OG_IMAGE_ABS` НЕ встановлена або пуста:

Шаблони (`base.html`, `landing.html`) автоматично генерують правильний URL:

```jinja2
{% set og_image_fallback = (request.url_root.rstrip('/') ~ url_for('static', filename='img/og-default.jpg')) %}
{% set og_image = config.OG_IMAGE_ABS if config.OG_IMAGE_ABS else og_image_fallback %}
```

**Результат:**
```
request.url_root = "https://marketing-agent-p4ig.onrender.com/"
url_for('static', filename='img/og-default.jpg') = "/static/img/og-default.jpg"
→ og_image = "https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg"
```

### Якщо `OG_IMAGE_ABS` = placeholder:
```
OG_IMAGE_ABS = "https://your-domain.com/static/img/og-default.jpg"
→ og_image = "https://your-domain.com/..." ❌ НЕ ІСНУЄ!
```

---

## 🛠️ Альтернативні методи

### Якщо немає доступу до Render прямо зараз:

Можна тимчасово виправити в коді (не рекомендується):

**app/config.py:**
```python
# Було:
OG_IMAGE_ABS = os.getenv("OG_IMAGE_ABS", "")

# Стало:
OG_IMAGE_ABS = ""  # Завжди використовувати автоматичний fallback
```

Commit → Push → Render автоматично задеплоїть

---

## 📊 Повний чек-лист

- [ ] Відкрити Render Dashboard
- [ ] Знайти Environment → OG_IMAGE_ABS
- [ ] Видалити змінну (або змінити на правильний URL)
- [ ] Дочекатись redeploy (~2-3 хв)
- [ ] Перевірити https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
- [ ] Facebook Debugger → Debug → Scrape Again
- [ ] ✅ Переконатись, що немає попереджень

---

## 🎯 Очікуваний результат

**До:**
```
❌ Недействительный тип контента изображения
❌ URL: https://your-domain.com/static/img/og-default.jpg
```

**Після:**
```
✅ og:image правильно встановлено
✅ Зображення доступне (200 OK)
✅ 1200x630px, JPEG, 70KB
✅ Facebook показує коректне прев'ю
✅ LinkedIn показує коректне прев'ю
```

---

## ⏱️ Загальний час виправлення

- **Видалення змінної на Render:** 30 секунд
- **Redeploy:** 2-3 хвилини
- **Facebook cache clear:** 1 хвилина
- **Загалом:** ~5 хвилин

---

## 🆘 Що робити, якщо не спрацювало?

### 1. Перевірте HTTP відповідь зображення

```bash
curl -I https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

**Має бути:**
```
HTTP/2 200
content-type: image/jpeg
content-length: 70753
```

**НЕ має бути:**
```
HTTP/2 404  ← зображення не знайдено
content-type: text/html  ← повертається HTML замість JPEG
```

### 2. Перевірте HTML сторінки

```bash
curl -s https://marketing-agent-p4ig.onrender.com | grep 'og:image'
```

**Має показати:**
```html
<meta property="og:image" content="https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg">
```

**НЕ має показати:**
```html
<meta property="og:image" content="https://your-domain.com/...">
```

### 3. Перевірте Render Environment

Переконайтесь, що:
- `OG_IMAGE_ABS` повністю видалена, або
- `OG_IMAGE_ABS` = `https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg`

### 4. Перевірте deployment logs

В Render Dashboard → Logs, перевірте, що:
- Deployment успішний
- Немає помилок при запуску Flask
- Gunicorn workers запущені

---

## 📚 Додаткова документація

- **Повна інструкція:** `docs/FIX_OG_IMAGE_ERROR.md`
- **Діагностичний скрипт:** `diagnose_og.py`
- **Тестування:** `verify_og_tags.py`

---

## ✅ Фінальна перевірка

Після всіх виправлень, переконайтесь:

1. ✅ `https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg` відкривається
2. ✅ Facebook Debugger → немає попереджень
3. ✅ LinkedIn Inspector → зображення відображається
4. ✅ `python diagnose_og.py` → все ✅
5. ✅ `python verify_og_tags.py` → Image accessible (Status: 200)

**Проблему вирішено! 🎉**

---

**ВАЖЛИВО:** Після виправлення Facebook може зберігати старий кеш до 24 годин. Використовуйте кнопку **"Scrape Again"** в Facebook Debugger для миттєвого оновлення!
