# Marketing SaaS Development Commands
# Nützliche PowerShell-Befehle für die Entwicklung

# Virtual Environment aktivieren
function Enable-Venv {
    .\.venv\Scripts\Activate.ps1
}

# Anwendung starten (Development)
function Start-App {
    $env:FLASK_APP = "run.py"
    $env:FLASK_DEBUG = "1"
    flask run
}

# Anwendung starten (Production-ähnlich)
function Start-Production {
    $env:FLASK_ENV = "production"
    $env:FLASK_DEBUG = "0"
    python run.py
}

# Datenbank-Migration erstellen
function New-Migration {
    param([string]$message = "Auto migration")
    flask db migrate -m $message
}

# Datenbank upgraden
function Update-Database {
    flask db upgrade
}

# Datenbank zurücksetzen (VORSICHT!)
function Reset-Database {
    $confirmation = Read-Host "Sind Sie sicher, dass Sie die Datenbank zurücksetzen möchten? (yes/no)"
    if ($confirmation -eq "yes") {
        Remove-Item "marketing.db" -ErrorAction SilentlyContinue
        Remove-Item "migrations" -Recurse -ErrorAction SilentlyContinue
        flask db init
        flask db migrate -m "Initial migration"
        flask db upgrade
        Write-Host "✅ Datenbank zurückgesetzt." -ForegroundColor Green
    }
}

# Dependencies aktualisieren
function Update-Dependencies {
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
}

# Neue Dependency hinzufügen
function Add-Dependency {
    param([string]$package)
    pip install $package
    pip freeze | Out-File requirements.txt -Encoding utf8
}

# Tests ausführen (wenn vorhanden)
function Invoke-Tests {
    python -m pytest tests/ -v
}

# Code-Qualität prüfen
function Test-Code {
    # Flake8 für Python Code Style
    flake8 app/ --max-line-length=88 --exclude=migrations
}

# Backup der Datenbank erstellen
function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "backup_$timestamp.db"
    Copy-Item "marketing.db" $backupName
    Write-Host "✅ Datenbank-Backup erstellt: $backupName" -ForegroundColor Green
}

# Logs anzeigen
function Show-Logs {
    Get-Content "app.log" -Tail 50 -Wait
}

# Alle Funktionen auflisten
function Show-Commands {
    Write-Host "📋 Verfügbare Befehle:" -ForegroundColor Cyan
    Write-Host "Enable-Venv            - Virtual Environment aktivieren" -ForegroundColor White
    Write-Host "Start-App              - Development Server starten" -ForegroundColor White
    Write-Host "Start-Production       - Production-ähnlicher Start" -ForegroundColor White
    Write-Host "New-Migration <msg>    - Neue Datenbank-Migration" -ForegroundColor White
    Write-Host "Update-Database        - Datenbank upgraden" -ForegroundColor White
    Write-Host "Reset-Database         - Datenbank zurücksetzen (VORSICHT!)" -ForegroundColor White
    Write-Host "Update-Dependencies    - Dependencies aktualisieren" -ForegroundColor White
    Write-Host "Add-Dependency <pkg>   - Neue Dependency hinzufügen" -ForegroundColor White
    Write-Host "Invoke-Tests           - Tests ausführen" -ForegroundColor White
    Write-Host "Test-Code              - Code-Qualität prüfen" -ForegroundColor White
    Write-Host "Backup-Database        - Datenbank-Backup erstellen" -ForegroundColor White
    Write-Host "Show-Logs              - Anwendungs-Logs anzeigen" -ForegroundColor White
    Write-Host "Show-Commands          - Diese Hilfe anzeigen" -ForegroundColor White
}

# Willkommensnachricht
Write-Host "🚀 Marketing SaaS Development Tools geladen!" -ForegroundColor Green
Write-Host "Verwenden Sie 'Show-Commands' um alle verfügbaren Befehle zu sehen." -ForegroundColor Yellow