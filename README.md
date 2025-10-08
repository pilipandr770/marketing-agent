# Marketing Automation SaaS

Eine vollständige Flask-basierte SaaS-Lösung für Marketing-Automatisierung mit KI-Integration, Multi-Platform Publishing und Stripe-Abrechnung.

## 🚀 Features

- **Multi-Tenant Architektur**: Skalierbar für viele Benutzer
- **KI-Content Generierung**: OpenAI GPT-4 für Text, DALL-E für Bilder, TTS für Audio
- **Multi-Platform Publishing**: Telegram (weitere Plattformen erweiterbar)
- **Intelligente Zeitplanung**: CRON-basierte automatische Posts
- **File Management**: Upload zu OpenAI Vector Stores
- **Stripe Integration**: Vollständige Abonnement-Verwaltung
- **Deutscher UI**: Professionelle Bootstrap-Oberfläche

## 📋 Voraussetzungen

- Python 3.8+
- Node.js (für eventuelle Frontend-Erweiterungen)
- Stripe Account
- OpenAI API Account
- Telegram Bot (optional, für Telegram-Publishing)

## 🛠️ Installation (Windows PowerShell)

### 1. Projekt klonen und Setup

```powershell
# Repository klonen
git clone <your-repo-url>
cd marketing-saas

# Virtual Environment erstellen
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Umgebungsvariablen konfigurieren

```powershell
# .env Datei erstellen
cp .env.example .env
```

Bearbeiten Sie `.env` mit Ihren API-Schlüsseln:

```env
# Flask Configuration
FLASK_SECRET_KEY=ihr-super-sicherer-secret-key-hier

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///marketing.db

# OpenAI
OPENAI_API_KEY=sk-ihr-openai-api-schluessel

# Stripe
STRIPE_PUBLIC_KEY=pk_test_ihr-stripe-public-key
STRIPE_SECRET_KEY=sk_test_ihr-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_ihr-webhook-secret
STRIPE_PRICE_BASIC=price_basic_plan_id
STRIPE_PRICE_PRO=price_pro_plan_id  
STRIPE_PRICE_ENTERPRISE=price_enterprise_plan_id

# Telegram (optional)
TELEGRAM_BOT_TOKEN=ihr-telegram-bot-token
```

### 3. Datenbank initialisieren

```powershell
# Flask Environment setzen
$env:FLASK_APP="run.py"
$env:FLASK_DEBUG="1"

# Datenbank-Migrationen erstellen
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Anwendung starten

```powershell
# Entwicklungsserver starten
flask run

# Oder direkt mit Python
python run.py
```

Die Anwendung ist unter `http://localhost:5000` verfügbar.

## 🔧 Stripe Setup

### 1. Stripe Produkte erstellen

1. Melden Sie sich bei Stripe Dashboard an
2. Erstellen Sie Produkte für Basic, Pro und Enterprise Pläne
3. Kopieren Sie die Price IDs in Ihre `.env` Datei

### 2. Webhook konfigurieren

1. Gehen Sie zu Stripe Dashboard > Webhooks
2. Fügen Sie Endpoint hinzu: `https://ihre-domain.com/billing/stripe/webhook`
3. Wählen Sie Events: `customer.subscription.*`, `invoice.payment_*`, `checkout.session.completed`
4. Kopieren Sie das Webhook Secret in `.env`

## 📱 Telegram Bot Setup (Optional)

1. Erstellen Sie einen Bot mit @BotFather
2. Erhalten Sie den Bot Token
3. Finden Sie Ihre Chat/Channel ID
4. Fügen Sie beide zu Ihren Benutzereinstellungen hinzu

## 🏗️ Architektur

```
app/
├── __init__.py              # Flask App Factory
├── extensions.py            # Flask Extensions
├── models.py               # SQLAlchemy Models
├── forms.py               # WTForms
├── openai_service.py      # OpenAI Integration
├── views/                 # Route Handlers
│   ├── auth.py           # Authentication
│   ├── dashboard.py      # User Dashboard
│   ├── content.py        # Content Generation
│   ├── schedule.py       # Scheduling System
│   └── files.py          # File Management
├── publishers/            # Social Media Publishers
│   ├── base.py          # Base Publisher Class
│   └── telegram_publisher.py
├── billing/              # Stripe Integration
│   ├── stripe_service.py
│   └── webhook.py
├── jobs/                 # Background Jobs
│   └── scheduler.py      # APScheduler
└── templates/           # Jinja2 Templates
    ├── base.html
    ├── auth/
    ├── dashboard/
    ├── content/
    ├── schedule/
    └── files/
```

## 🌟 Key Features im Detail

### Multi-Tenancy
- Jeder Benutzer hat isolierte Daten
- Sichere Trennung von API-Schlüsseln
- Skalierbare Architektur

### Content Generation
- GPT-4 für intelligente Texterstellung
- DALL-E für Bildgenerierung
- TTS für Audioausgabe
- Plattform-spezifische Optimierung

### Scheduling System
- CRON-basierte Zeitplanung
- Echtzeitvalidierung von CRON-Ausdrücken
- Automatische Job-Verwaltung mit APScheduler

### Billing System
- Vollständige Stripe-Integration
- Webhook-basierte Synchronisation
- Plan-basierte Feature-Limits
- Customer Portal Integration

## 🔒 Sicherheit

- CSRF-Schutz auf allen Formularen
- Sichere Passwort-Hashing
- Input-Validierung und Sanitization
- SQL-Injection Schutz durch SQLAlchemy
- Sichere File-Upload Handling

## 📊 Monitoring & Logging

- Strukturiertes Logging für alle Module
- Error Tracking für OpenAI und Stripe APIs
- Scheduler Job Monitoring
- User Activity Tracking

## 🚀 Deployment

### Lokale Entwicklung
```powershell
flask run
```

### Production (Beispiel mit Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Environment Variables für Production
- `FLASK_ENV=production`
- `SQLALCHEMY_DATABASE_URI=postgresql://...` (für PostgreSQL)
- Alle API Keys sicher konfigurieren

## 🔄 Erweiterungen

### Neue Social Media Plattformen hinzufügen
1. Erstellen Sie neue Publisher-Klasse in `publishers/`
2. Erweitern Sie User-Model um neue Konfigurationsfelder
3. Aktualisieren Sie UI-Formulare und Templates

### Neue Payment Provider
1. Erstellen Sie Service-Klasse analog zu `stripe_service.py`
2. Implementieren Sie Webhook-Handler
3. Erweitern Sie Billing-Templates

## 📞 Support

Bei Fragen oder Problemen:
- Dokumentation durchgehen
- Issues im Repository erstellen
- Community-Forum nutzen

## 📄 Lizenz

MIT License - Siehe LICENSE Datei für Details.

## 🙏 Credits

- Flask & Extensions Team
- OpenAI für KI-Services  
- Stripe für Payment Processing
- Bootstrap für UI-Framework
- Alle Open Source Contributors