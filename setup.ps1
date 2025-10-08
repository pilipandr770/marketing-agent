# Windows PowerShell Setup Script für Marketing SaaS
# Führen Sie dieses Skript im Projektverzeichnis aus

Write-Host "🚀 Marketing SaaS Setup wird gestartet..." -ForegroundColor Green

# Prüfen ob Python installiert ist
try {
    $pythonVersion = py -3 --version
    Write-Host "✅ Python gefunden: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 nicht gefunden. Bitte Python 3.8+ installieren." -ForegroundColor Red
    exit 1
}

# Virtual Environment erstellen
Write-Host "🔧 Virtual Environment wird erstellt..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️  Virtual Environment existiert bereits." -ForegroundColor Yellow
} else {
    py -3 -m venv .venv
    Write-Host "✅ Virtual Environment erstellt." -ForegroundColor Green
}

# Virtual Environment aktivieren
Write-Host "🔧 Virtual Environment wird aktiviert..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Dependencies installieren
Write-Host "📦 Dependencies werden installiert..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ Dependencies installiert." -ForegroundColor Green

# .env Datei erstellen wenn nicht vorhanden
if (-not (Test-Path ".env")) {
    Write-Host "🔧 .env Datei wird erstellt..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Bitte .env Datei mit Ihren API-Schlüsseln konfigurieren!" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env Datei existiert bereits." -ForegroundColor Green
}

# Upload Ordner erstellen
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads"
    Write-Host "✅ Upload-Ordner erstellt." -ForegroundColor Green
}

# Flask Environment setzen
$env:FLASK_APP = "run.py"
$env:FLASK_DEBUG = "1"

# Datenbank initialisieren
Write-Host "🗄️  Datenbank wird initialisiert..." -ForegroundColor Yellow

try {
    # Prüfen ob migrations Ordner existiert
    if (-not (Test-Path "migrations")) {
        flask db init
        Write-Host "✅ Datenbank-Migrationen initialisiert." -ForegroundColor Green
    }
    
    # Migration erstellen und ausführen
    flask db migrate -m "Initial setup"
    flask db upgrade
    Write-Host "✅ Datenbank konfiguriert." -ForegroundColor Green
} catch {
    Write-Host "⚠️  Datenbank-Setup Fehler. Möglicherweise bereits konfiguriert." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup abgeschlossen!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Nächste Schritte:" -ForegroundColor Cyan
Write-Host "1. Konfigurieren Sie Ihre API-Schlüssel in der .env Datei" -ForegroundColor White
Write-Host "2. Starten Sie die Anwendung mit: flask run" -ForegroundColor White
Write-Host "3. Öffnen Sie http://localhost:5000 in Ihrem Browser" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Wichtige API-Schlüssel die Sie benötigen:" -ForegroundColor Cyan
Write-Host "- OpenAI API Key (für KI-Features)" -ForegroundColor White
Write-Host "- Stripe Keys (für Zahlungen)" -ForegroundColor White
Write-Host "- Telegram Bot Token (optional, für Telegram-Publishing)" -ForegroundColor White
Write-Host ""
Write-Host "📚 Weitere Informationen in der README.md" -ForegroundColor Cyan