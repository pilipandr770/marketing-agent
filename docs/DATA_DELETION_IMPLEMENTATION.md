# Data Deletion Implementation (GDPR & Meta Requirement)

## 📋 Огляд

Реалізовано повну систему управління даними користувача згідно з вимогами:
- **GDPR** (General Data Protection Regulation)
- **Meta/Facebook** (обов'язкова вимога для Facebook App)
- **Прозорість** для користувачів

---

## 🎯 Функціональність

### 1. **Сторінка видалення даних**
**URL:** `/data-deletion`
**Шаблон:** `app/templates/data_deletion.html`

### Можливості:

#### 📊 Для автентифікованих користувачів:
1. **Перегляд даних** - огляд збережених даних
2. **Експорт даних** (GDPR Article 20) - завантаження всіх даних у JSON
3. **Видалення API ключів** - очищення токенів без видалення акаунту
4. **Видалення контенту** - видалення zeitpläne та файлів
5. **Повне видалення акаунту** (GDPR Article 17) - незворотнє видалення

#### 📧 Для неавтентифікованих:
- Форма запиту на видалення через email
- Інструкції для видалення Facebook App даних

---

## 🔧 Технічна реалізація

### Routes (app/views/dashboard.py):

#### 1. `/dashboard/export-data` (GET)
```python
@dashboard_bp.route("/export-data")
@login_required
def export_user_data():
```
**Що робить:**
- Збирає всі дані користувача (профіль, налаштування, zeitpläne, файли, контент)
- Експортує у JSON формат
- Повертає файл для завантаження

**GDPR:** Article 20 - Right to data portability

---

#### 2. `/dashboard/delete-api-keys` (POST)
```python
@dashboard_bp.route("/delete-api-keys", methods=["POST"])
@login_required
def delete_api_keys():
```
**Що видаляє:**
- OpenAI API Key
- Telegram Bot Token
- LinkedIn Access Token
- Meta (Facebook/Instagram) Access Token

**Результат:** Користувач залишається, API ключі видалені

---

#### 3. `/dashboard/delete-content` (POST)
```python
@dashboard_bp.route("/delete-content", methods=["POST"])
@login_required
def delete_user_content():
```
**Що видаляє:**
- Всі zeitpläne (Schedule)
- Всі файли (filesystem + database)
- Весь згенерований контент (GeneratedContent)

**Результат:** Користувач і API ключі залишаються

---

#### 4. `/dashboard/delete-account` (POST)
```python
@dashboard_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
```
**Що видаляє (ПОВНІСТЮ):**
1. Файли з файлової системи
2. UserFile records
3. Schedule records
4. GeneratedContent records
5. Subscription records
6. User account

**Підтвердження:** Вимагає введення email
**Результат:** Повне видалення + автоматичний logout
**GDPR:** Article 17 - Right to erasure

---

## 📱 UI/UX

### Сторінка data_deletion.html містить:

#### Для автентифікованих:
- **Information Card** - пояснення GDPR прав
- **Account Overview** - поточні дані користувача
- **Action Buttons:**
  - 🔵 Експорт даних (JSON)
  - 🟡 Видалити API ключі
  - 🟡 Видалити контент
  - 🔴 Видалити акаунт

#### Modals (підтвердження):
- **deleteApiKeysModal** - попередження про наслідки
- **deleteContentModal** - підтвердження з кількістю даних
- **deleteAccountModal** - критичне попередження + email confirmation

---

## 🔗 Інтеграція в додаток

### 1. Footer (base.html)
```html
<a href="{{ url_for('public.data_deletion') }}">Daten löschen</a>
```

### 2. User Menu (base.html)
```html
<li><a href="{{ url_for('public.data_deletion') }}">
    <i class="bi bi-shield-exclamation"></i> Daten verwalten
</a></li>
```

### 3. AGB (agb.html)
```html
<div class="alert alert-info">
    Ihre Datenschutzrechte → Zur Datenlöschung
</div>
```

---

## 🌐 Meta/Facebook Integration

### Facebook App Settings Instructions:
Сторінка містить покрокову інструкцію для видалення даних через Facebook:

1. Зайти в Facebook Settings
2. Apps and Websites
3. Знайти "Marketing Agent"
4. Клікнути "Remove"

**Посилання:** https://www.facebook.com/settings?tab=applications

---

## 🛡️ GDPR Compliance

### Реалізовані права:

✅ **Article 15** - Right to access (export data)
✅ **Article 17** - Right to erasure (delete account)
✅ **Article 20** - Right to data portability (JSON export)
✅ **Article 21** - Right to object (partial deletion)

### Логування:
Всі дії видалення логуються:
```python
logger.info(f"User {current_user.email} exported their data")
logger.info(f"User {current_user.email} deleted all API keys")
logger.info(f"User account deleted: {user_email} (ID: {user_id})")
```

---

## 📊 Що зберігається в експорті JSON

```json
{
  "export_date": "2025-10-11T...",
  "user": {
    "email": "user@example.com",
    "created_at": "2025-01-01T...",
    "is_premium": false,
    "subscription_tier": null
  },
  "settings": {
    "has_openai_key": true,
    "has_telegram_token": true,
    "linkedin_urn": "...",
    "facebook_page_id": "...",
    "instagram_business_id": "..."
  },
  "schedules": [...],
  "files": [...],
  "generated_content": [...]
}
```

**Примітка:** API ключі НЕ експортуються (лише факт наявності)

---

## 🧪 Тестування

### Перевірити функціонал:

1. **Експорт даних:**
   ```
   1. Логін → /data-deletion
   2. Клік "Daten exportieren"
   3. Перевірити JSON файл
   ```

2. **Видалення API ключів:**
   ```
   1. Логін → /data-deletion
   2. Клік "API-Keys löschen"
   3. Підтвердити в modal
   4. Перевірити Settings (мають бути пусті)
   ```

3. **Видалення контенту:**
   ```
   1. Логін → /data-deletion
   2. Клік "Zeitpläne und Dateien löschen"
   3. Підтвердити
   4. Перевірити Schedule/Files (мають бути видалені)
   ```

4. **Видалення акаунту:**
   ```
   1. Логін → /data-deletion
   2. Клік "Konto vollständig löschen"
   3. Ввести email для підтвердження
   4. Підтвердити
   5. → Автоматичний logout + redirect на landing
   ```

---

## 🚨 Безпека

### Захист від випадкового видалення:

1. **Email Confirmation** - для видалення акаунту
2. **Modals** - попередження перед кожною дією
3. **CSRF Protection** - всі POST запити захищені
4. **@login_required** - тільки автентифіковані користувачі

---

## 📧 Контакт для запитів

Якщо користувач не може зайти в акаунт:
```
support@andriit.de
Тема: "Datenlöschung Marketing Agent"
```

---

## 🎯 Meta App Review Requirements

### Для проходження Meta App Review потрібно:

✅ **Data Deletion URL:**
```
https://marketing-agent-p4ig.onrender.com/data-deletion
```

✅ **Instructions:**
- Покрокова інструкція присутня на сторінці
- Посилання на Facebook App Settings

✅ **Email Alternative:**
- Можливість запиту через email

### Додати в Facebook App Settings:
1. App Dashboard → Settings → Basic
2. Знайти "User Data Deletion"
3. Додати URL: `https://marketing-agent-p4ig.onrender.com/data-deletion`
4. Або: `mailto:support@andriit.de`

---

## 📚 Файли створені/змінені

### Нові файли:
- `app/templates/data_deletion.html` - головна сторінка

### Змінені файли:
- `app/views/public.py` - роут `/data-deletion`
- `app/views/dashboard.py` - роути для експорту та видалення
- `app/templates/base.html` - footer + user menu links
- `app/templates/agb.html` - GDPR alert з посиланням

---

## ✅ Висновок

Реалізовано повноцінну систему управління даними користувача:
- ✅ GDPR compliance (Articles 15, 17, 20, 21)
- ✅ Meta/Facebook вимоги виконані
- ✅ Прозорість для користувачів
- ✅ Безпека (email confirmation, CSRF)
- ✅ Логування всіх операцій
- ✅ UI/UX з попередженнями

**Готово до Meta App Review! 🚀**
