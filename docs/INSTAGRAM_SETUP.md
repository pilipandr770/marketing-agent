# Instagram Конфігурація - Інструкція

## Статус: "Instagram ist nicht konfiguriert"

Це повідомлення з'являється тому, що для публікації в Instagram потрібна Meta OAuth авторизація та налаштування Instagram Business акаунту.

---

## 📋 Що потрібно для Instagram публікації?

### 1. Facebook App Domain (КРИТИЧНО!)

В налаштуваннях Facebook App додайте домен:

**URL:** https://developers.facebook.com/apps/

**Кроки:**
1. Відкрийте ваш Facebook App
2. Перейдіть до **"Settings"** → **"Basic"**
3. Знайдіть **"App Domains"**
4. Додайте: `marketing-agent-p4ig.onrender.com`
5. Збережіть зміни

### 2. Redirect URIs (OAuth Settings)

В розділі **"Products"** → **"Facebook Login"** → **"Settings"**:

**Valid OAuth Redirect URIs:**
```
https://marketing-agent-p4ig.onrender.com/meta/callback
```

---

## 🔧 Environment Variables на Render

Додайте наступні змінні в **Environment** секції на Render:

```bash
META_APP_ID=your_facebook_app_id_here
META_APP_SECRET=your_facebook_app_secret_here
```

**Де знайти ці дані?**
- Facebook App Dashboard → Settings → Basic
- **App ID** - видно одразу
- **App Secret** - натисніть "Show" для перегляду

---

## 📸 Instagram Business Account

Instagram публікація працює тільки з **Instagram Business** або **Creator** акаунтами, які підключені до Facebook Page.

### Перевірка:
1. Відкрийте Instagram app
2. Перейдіть до **Profile** → **Settings** → **Account**
3. Має бути опція **"Switch to Professional Account"**
4. Якщо вже є - має показувати **"Business"** або **"Creator"**

### Підключення до Facebook Page:
1. Instagram app → Settings → Business
2. **"Connect to Facebook Page"**
3. Виберіть вашу Facebook сторінку
4. Підтвердіть підключення

---

## 🚀 Як підключити Instagram в додатку?

### Крок 1: Авторизація через Meta OAuth

1. Відкрийте додаток: https://marketing-agent-p4ig.onrender.com
2. Перейдіть до **Dashboard** → **Settings**
3. Натисніть **"Mit Meta verbinden"** (Connect with Meta)
4. Авторизуйтесь через Facebook
5. **ВАЖЛИВО:** Надайте дозволи:
   - `pages_show_list` - список Pages
   - `pages_read_engagement` - читання даних
   - `pages_manage_posts` - публікація постів
   - `instagram_basic` - базовий доступ
   - `instagram_content_publish` - публікація контенту

### Крок 2: Вибір Instagram Business Account

Після успішної авторизації:
1. Система автоматично знайде ваші Facebook Pages
2. З кожної Page буде витягнуто підключений Instagram Business ID
3. Ви зможете вибрати потрібний акаунт

### Крок 3: Публікація

Після підключення:
1. Перейдіть до **Content Generator**
2. Створіть контент
3. Виберіть платформу **"Instagram"**
4. Натисніть **"Veröffentlichen"** (Publish)

---

## ⚠️ Обмеження Instagram API

### Що можна публікувати:
- ✅ Фото (JPEG, до 8MB)
- ✅ Відео (MP4, до 100MB, 3-60 секунд)
- ✅ Карусель (до 10 фото/відео)
- ✅ Caption (текст до 2200 символів)
- ✅ Hashtags

### Що НЕ можна:
- ❌ Stories (потрібен окремий API)
- ❌ Reels через API (потрібна мобільна авторизація)
- ❌ IGTV довгі відео
- ❌ Прямі ефіри

### Rate Limits:
- 25 публікацій на день на Instagram Business Account
- 50 API викликів на годину

---

## 🔍 Поточний стан вашого додатку

### ✅ Що вже працює:
1. Telegram Publisher - працює
2. LinkedIn OAuth - працює (ви вже підключили)
3. Meta OAuth код - реалізовано
4. Database - columns для Instagram готові

### 🔄 Що потрібно налаштувати:
1. Facebook App Domain - `marketing-agent-p4ig.onrender.com`
2. META_APP_ID та META_APP_SECRET в Render ENV
3. Instagram Business Account підключений до Facebook Page
4. Авторизація через Meta OAuth в додатку

---

## 🛠️ Альтернативний метод (якщо OAuth не працює)

### Ручне введення токена:

1. Отримайте Long-Lived User Access Token:
   - Facebook Graph API Explorer: https://developers.facebook.com/tools/explorer/
   - Виберіть ваш App
   - Запросіть токен з permissions: `pages_show_list`, `instagram_basic`, `instagram_content_publish`
   - Натисніть "Generate Access Token"

2. Конвертуйте в Long-Lived (60 днів):
   ```bash
   curl -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

3. Отримайте Instagram Business Account ID:
   ```bash
   curl -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token=LONG_LIVED_TOKEN"
   # Візьміть page_access_token для потрібної Page
   
   curl -X GET "https://graph.facebook.com/v21.0/PAGE_ID?fields=instagram_business_account&access_token=PAGE_ACCESS_TOKEN"
   ```

4. Збережіть в базі даних:
   - `meta_access_token` = PAGE_ACCESS_TOKEN
   - `instagram_business_id` = ID з попереднього запиту

---

## 📚 Корисні посилання

- **Facebook App Dashboard:** https://developers.facebook.com/apps/
- **Instagram Business API Docs:** https://developers.facebook.com/docs/instagram-api/
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **Access Token Debugger:** https://developers.facebook.com/tools/debug/accesstoken/

---

## 🎯 Очікуваний результат

Після налаштування:

**До:**
```
❌ Instagram ist nicht konfiguriert. Content wurde nur generiert.
```

**Після:**
```
✅ Content erfolgreich auf Instagram veröffentlicht!
```

---

## 🆘 Що робити при помилках?

### "Invalid OAuth redirect URI"
- Перевірте, що в Facebook App додано правильний redirect URI
- Переконайтесь, що домен додано в App Domains

### "Instagram account is not a Business account"
- Конвертуйте акаунт в Business/Creator
- Підключіть до Facebook Page

### "Missing permissions"
- При OAuth авторизації надайте всі запитані дозволи
- Перевірте в App Review, що потрібні permissions активовані

---

**Наступний крок:** Налаштуйте Facebook App Domain і додайте ENV змінні на Render! 🚀
