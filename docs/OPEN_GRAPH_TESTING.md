# Open Graph Testing Guide

## Що було реалізовано

### 1. **app/config.py** - Централізована конфігурація
- Open Graph налаштування (title, description, image, locale)
- Meta Pixel ID
- Всі існуючі налаштування Flask, Stripe, Database

### 2. **app/templates/base.html** - Meta теги
✅ **Open Graph теги** (для Facebook, LinkedIn):
- `og:type` = website
- `og:site_name` = Andrii-IT
- `og:locale` = de_DE (з альтернативою uk_UA)
- `og:url` = поточний URL сторінки
- `og:title` = Marketing Agent - KI-gestützte Marketing Automation
- `og:description` = опис з 3 соцмережами
- `og:image` = абсолютний URL зображення (1200x630px)
- `og:image:width` = 1200
- `og:image:height` = 630
- `og:image:type` = image/jpeg

✅ **Twitter Card** (для X/Twitter):
- `twitter:card` = summary_large_image
- `twitter:title`, `twitter:description`, `twitter:image`

✅ **Meta Pixel** (Facebook аналітика):
- Інтеграція fbq() з кастомними подіями
- `app/static/js/pixel.js` - helper функції для трекінгу

### 3. **Зображення**
- `app/static/img/og-default.jpg` - 1200x630px (69KB)
- `app/static/img/favicon.png` - 64x64px

---

## Тестування Open Graph

### 1️⃣ Facebook Sharing Debugger
**URL:** https://developers.facebook.com/tools/debug/

**Кроки:**
1. Введіть URL вашого сайту: `https://marketing-agent-p4ig.onrender.com`
2. Натисніть **"Debug"**
3. Перевірте, що:
   - ✅ `og:image` відображається (1200x630px)
   - ✅ `og:title` правильний
   - ✅ `og:description` присутній
   - ✅ Немає попереджень або помилок

**Якщо зображення не оновлюється:**
- Натисніть **"Scrape Again"** для оновлення кешу Facebook

---

### 2️⃣ LinkedIn Post Inspector
**URL:** https://www.linkedin.com/post-inspector/

**Кроки:**
1. Введіть URL: `https://marketing-agent-p4ig.onrender.com`
2. Натисніть **"Inspect"**
3. Перевірте прев'ю картки:
   - Зображення, заголовок, опис

**Примітка:** LinkedIn кешує OG-теги на 7 днів. Використовуйте Inspector для очищення кешу.

---

### 3️⃣ Twitter Card Validator
**URL:** https://cards-dev.twitter.com/validator

**Кроки:**
1. Введіть URL сайту
2. Натисніть **"Preview card"**
3. Перевірте `summary_large_image` картку

---

### 4️⃣ OpenGraph.xyz (загальний інструмент)
**URL:** https://www.opengraph.xyz/

**Кроки:**
1. Введіть URL
2. Перегляньте, як виглядає прев'ю на різних платформах (Facebook, Twitter, Slack, Discord)

---

### 5️⃣ Локальне тестування HTML

Перевірте `<head>` вашої сторінки:

```bash
curl https://marketing-agent-p4ig.onrender.com | grep "og:"
```

**Очікуваний результат:**
```html
<meta property="og:type" content="website">
<meta property="og:site_name" content="Andrii-IT">
<meta property="og:locale" content="de_DE">
<meta property="og:url" content="https://marketing-agent-p4ig.onrender.com/">
<meta property="og:title" content="Marketing Agent - KI-gestützte Marketing Automation">
<meta property="og:description" content="Erstellen und veröffentlichen Sie professionelle Social-Media-Inhalte automatisch auf Telegram, Facebook, Instagram und LinkedIn mit OpenAI-Technologie.">
<meta property="og:image" content="https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/jpeg">
```

---

## Налаштування через ENV (Render.com)

Додайте у **Environment Variables** на Render:

```bash
# Open Graph (опціонально - дефолти вже є в config.py)
OG_SITE_NAME=Andrii-IT
OG_TITLE=Marketing Agent - KI-gestützte Marketing Automation
OG_DESCRIPTION=Erstellen und veröffentlichen Sie professionelle Social-Media-Inhalte automatisch auf Telegram, Facebook, Instagram und LinkedIn mit OpenAI-Technologie.
OG_IMAGE_ABS=https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg
OG_LOCALE=de_DE

# Meta Pixel (опціонально)
META_PIXEL_ID=your_pixel_id_here
```

**Примітка:** Якщо не задати `OG_IMAGE_ABS`, система автоматично згенерує URL з `request.url_root`.

---

## Використання Meta Pixel

### Tracking Events у JS

Після того, як користувач виконає певну дію, можна відслідковувати події:

```javascript
// В будь-якому JS коді (наприклад, content.html)

// 1. Генерація контенту
trackContentGeneration('telegram', 'post');

// 2. Публікація контенту
trackContentPublish('linkedin');

// 3. Підписка на план
trackSubscription('Pro Plan');

// 4. Лід (реєстрація)
trackLead();
```

Функції доступні глобально після завантаження `pixel.js`.

---

## Часті помилки та рішення

### ❌ "Missing og:image"
**Причина:** Зображення не доступне або неправильний URL

**Рішення:**
1. Перевірте, що файл існує: `app/static/img/og-default.jpg`
2. Перевірте доступність: `curl -I https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg`
3. Має повертати `200 OK`

---

### ❌ "Image is too small"
**Причина:** Facebook вимагає мінімум 200x200px (рекомендовано 1200x630px)

**Рішення:**
- Використовуйте `create_og_image.py` для створення правильного розміру
- Або завантажте власне зображення 1200x630px

---

### ❌ "Could not scrape URL"
**Причина:** Сайт недоступний або блокує боти

**Рішення:**
1. Перевірте, що сайт працює: `curl -I https://marketing-agent-p4ig.onrender.com`
2. Переконайтесь, що немає robots.txt блокування для Facebook/LinkedIn ботів

---

### ❌ "Incomplete meta tags"
**Причина:** Не всі обов'язкові OG теги присутні

**Рішення:**
- Перевірте, що `base.html` містить всі теги з шаблону
- Обов'язкові: `og:title`, `og:type`, `og:image`, `og:url`

---

## Додаткові можливості

### 1. Динамічний OG для різних сторінок

В окремих template можна перевизначити OG теги:

```jinja2
{% extends "base.html" %}

{% block extra_head %}
  <meta property="og:title" content="Custom Page Title">
  <meta property="og:description" content="Custom description">
{% endblock %}
```

### 2. Різні зображення для різних сторінок

```python
# У вашому view
@app.route('/blog/<slug>')
def blog_post(slug):
    post = get_post(slug)
    og_image = url_for('static', filename=f'img/blog/{post.image}', _external=True)
    return render_template('blog_post.html', post=post, og_image=og_image)
```

```jinja2
{% if og_image %}
  <meta property="og:image" content="{{ og_image }}">
{% endif %}
```

---

## Корисні посилання

- **Facebook Debugger:** https://developers.facebook.com/tools/debug/
- **LinkedIn Inspector:** https://www.linkedin.com/post-inspector/
- **Twitter Validator:** https://cards-dev.twitter.com/validator
- **OpenGraph Protocol:** https://ogp.me/
- **Meta Pixel Setup:** https://www.facebook.com/business/tools/meta-pixel

---

## Підсумок

✅ Open Graph теги додані у `base.html`  
✅ Конфігурація централізована у `app/config.py`  
✅ Зображення og-default.jpg створено (1200x630px)  
✅ Favicon додано  
✅ Meta Pixel інтегрований з кастомними подіями  
✅ Twitter Card підтримка  

**Наступний крок:** Протестуйте на Facebook Sharing Debugger та LinkedIn Post Inspector! 🚀
