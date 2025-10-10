# 🔧 Виправлення "Недействительный тип контента изображения"

## Проблема

Facebook Sharing Debugger показує помилку:
```
⚠️ Недействительный тип контента изображения
URL, указанный для og:image (https://your-domain.com/static/img/og-default.jpg), 
невозможно обработать как изображение. Недействительный тип контента.
```

## Причина

В Environment Variables на Render встановлено `OG_IMAGE_ABS` з placeholder URL `https://your-domain.com/...` замість реального домену.

---

## ✅ Рішення 1: Видалити OG_IMAGE_ABS з Render ENV (РЕКОМЕНДОВАНО)

### Крок 1: Відкрийте Render Dashboard
https://dashboard.render.com/

### Крок 2: Виберіть ваш сервіс
`marketing-agent-p4ig`

### Крок 3: Перейдіть до Environment
Ліва панель → **"Environment"**

### Крок 4: Видаліть OG_IMAGE_ABS
Якщо змінна `OG_IMAGE_ABS` існує:
1. Знайдіть її в списку
2. Натисніть **"Delete"** (іконка смітника)
3. Підтвердіть видалення

### Крок 5: Redeploy (автоматично)
Render автоматично перезапустить сервіс після видалення змінної.

### Чому це працює?
Якщо `OG_IMAGE_ABS` не встановлена (або пуста), додаток автоматично використає fallback:
```jinja2
{% set og_image_fallback = (request.url_root.rstrip('/') ~ url_for('static', filename='img/og-default.jpg')) %}
{% set og_image = config.OG_IMAGE_ABS if config.OG_IMAGE_ABS else og_image_fallback %}
```

**Результат:** `https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg`

---

## ✅ Рішення 2: Виправити OG_IMAGE_ABS на правильний URL

Якщо ви хочете явно задати URL зображення:

### Крок 1-3: Те саме, що вище

### Крок 4: Змініть значення
Знайдіть `OG_IMAGE_ABS` і змініть на:
```
https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

### Крок 5: Save Changes
Натисніть **"Save Changes"**

### Крок 6: Дочекайтесь redeploy

---

## 🧪 Перевірка після виправлення

### 1. Перевірте доступність зображення

Відкрийте в браузері:
```
https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

**Очікуваний результат:** Зображення 1200x630px відкривається

**Перевірте HTTP заголовки:**
```bash
curl -I https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

Має бути:
```
HTTP/2 200
content-type: image/jpeg
content-length: 70753
```

---

### 2. Перевірте HTML meta теги

Відкрийте в браузері:
```
https://marketing-agent-p4ig.onrender.com
```

Перегляньте код сторінки (Ctrl+U або Cmd+Option+U), знайдіть:
```html
<meta property="og:image" content="https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg">
```

**НЕ має бути:**
```html
<meta property="og:image" content="https://your-domain.com/static/img/og-default.jpg">
```

---

### 3. Facebook Sharing Debugger (фінальна перевірка)

**URL:** https://developers.facebook.com/tools/debug/

1. Введіть: `https://marketing-agent-p4ig.onrender.com`
2. Натисніть **"Debug"**
3. Якщо старий URL ще в кеші, натисніть **"Scrape Again"**

**Очікуваний результат:**
```
✅ Image: https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
✅ Image Width: 1200
✅ Image Height: 630
✅ Image Type: image/jpeg
❌ Немає попереджень!
```

---

## 🔍 Діагностика

### Перевірка поточного значення OG_IMAGE_ABS

Запустіть локально:
```python
# test_og_config.py
from app import create_app

app = create_app()
with app.app_context():
    print(f"OG_IMAGE_ABS: {app.config.get('OG_IMAGE_ABS')}")
```

```bash
python test_og_config.py
```

**Очікувані результати:**
- ✅ `OG_IMAGE_ABS: ` (пусто - використається fallback)
- ✅ `OG_IMAGE_ABS: https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg`
- ❌ `OG_IMAGE_ABS: https://your-domain.com/...` (ПОТРІБНО ВИПРАВИТИ!)

---

## 📝 Альтернативний метод: Локальна перевірка

Використайте скрипт `verify_og_tags.py`:

```bash
python verify_og_tags.py
```

Перевірте секцію:
```
🖼️  Checking og:image accessibility: https://...
   ✅ Image accessible (Status: 200)
   📦 Content-Type: image/jpeg
```

Якщо побачите:
```
❌ Image not accessible (Status: 404)
```
Або URL містить `your-domain.com` - треба виправляти ENV на Render.

---

## 🎯 Швидке виправлення (якщо немає доступу до Render)

Якщо ви не можете змінити ENV на Render прямо зараз, можна тимчасово виправити в коді:

### Варіант A: Завжди використовувати fallback

`app/config.py`:
```python
# Закоментуйте або видаліть цю лінію:
# OG_IMAGE_ABS = os.getenv("OG_IMAGE_ABS", "")

# Замініть на:
OG_IMAGE_ABS = ""  # Завжди використовувати fallback
```

### Варіант B: Hardcode правильний URL

`app/config.py`:
```python
OG_IMAGE_ABS = os.getenv("OG_IMAGE_ABS", "https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg")
```

**Після зміни:**
```bash
git add app/config.py
git commit -m "Fix: Use correct domain for OG_IMAGE_ABS"
git push
```

---

## ⏱️ Таймінг виправлення

- **Видалення ENV на Render:** 30 секунд
- **Redeploy:** ~2-3 хвилини
- **Facebook cache clear:** 1 хвилина
- **Загальний час:** ~5 хвилин

---

## 🆘 Що робити, якщо помилка залишається?

### 1. Очистіть кеш Facebook
В Facebook Debugger натисніть **"Scrape Again"** 2-3 рази

### 2. Перевірте HTTP заголовки зображення
```bash
curl -I https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
```

Має бути:
- `HTTP/2 200` (не 404, не 500)
- `content-type: image/jpeg` (не `text/html`)

### 3. Перевірте розмір зображення
```bash
curl -s https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg | wc -c
```

Має бути ~70000 байт (70KB)

### 4. Перевірте, що файл існує на сервері
Через SSH (якщо доступний) або через logs:
```bash
ls -lh app/static/img/og-default.jpg
```

---

## ✅ Фінальна перевірка

Після всіх виправлень:

1. ✅ `curl -I https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg` → 200 OK
2. ✅ Facebook Debugger → немає попереджень
3. ✅ LinkedIn Inspector → зображення відображається
4. ✅ `verify_og_tags.py` → всі ✅

**Готово! Проблему вирішено! 🎉**

---

## 📚 Корисні команди

### Перевірка всіх OG тегів разом
```bash
curl -s https://marketing-agent-p4ig.onrender.com | grep -E '(og:|twitter:)' | head -20
```

### Перевірка тільки og:image
```bash
curl -s https://marketing-agent-p4ig.onrender.com | grep 'og:image'
```

### Скачати зображення локально для перевірки
```bash
curl -o test-og-image.jpg https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
file test-og-image.jpg  # Має показати: JPEG image data, 1200 x 630
```

---

**Рекомендація:** Видаліть `OG_IMAGE_ABS` з Render ENV, щоб завжди використовувати автоматичний fallback! 🚀
