# file: app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
import re

class RegisterForm(FlaskForm):
    email = StringField("E-Mail-Adresse", validators=[DataRequired(), Email()])
    password = PasswordField("Passwort", validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField("Passwort bestätigen", validators=[DataRequired()])
    submit = SubmitField("Konto erstellen")

    def validate_password_confirm(self, field):
        if field.data != self.password.data:
            raise ValidationError("Passwörter stimmen nicht überein.")

class LoginForm(FlaskForm):
    email = StringField("E-Mail-Adresse", validators=[DataRequired(), Email()])
    password = PasswordField("Passwort", validators=[DataRequired()])
    remember_me = BooleanField("Angemeldet bleiben")
    submit = SubmitField("Anmelden")

class SettingsForm(FlaskForm):
    # Telegram settings
    telegram_token = StringField("Telegram Bot Token", validators=[Optional()])
    telegram_chat_id = StringField("Telegram Chat/Kanal ID", validators=[Optional()], 
                                   description="@kanalname oder numerische ID")
    
    # OpenAI settings
    openai_system_prompt = TextAreaField("System-Anweisungen für KI-Modell", 
                                         validators=[Optional()], 
                                         description="Zusätzliche Anweisungen für die Content-Generierung")
    openai_api_key = StringField("Eigener OpenAI API-Schlüssel (optional)", validators=[Optional()])
    
    submit = SubmitField("Einstellungen speichern")

class ScheduleForm(FlaskForm):
    channel = SelectField("Plattform", 
                         choices=[("telegram", "Telegram"), ("facebook", "Facebook"), 
                                ("linkedin", "LinkedIn"), ("instagram", "Instagram")],
                         validators=[DataRequired()])
    
    cron_expression = StringField("Zeitplan (CRON)", validators=[DataRequired()],
                                 description="z.B. '0 9 * * *' für täglich 9:00 Uhr")
    
    content_template = TextAreaField("Content-Vorlage", validators=[DataRequired()],
                                    description="Thema oder Briefing für automatische Content-Erstellung")
    
    generate_image = BooleanField("Bild automatisch generieren")
    generate_voice = BooleanField("Sprachausgabe generieren")
    
    content_type = SelectField("Content-Typ",
                              choices=[("post", "Standard Post"), ("story", "Story"), ("reel", "Reel/Video")],
                              default="post")
    
    active = BooleanField("Zeitplan aktiv", default=True)
    submit = SubmitField("Zeitplan speichern")

    def validate_cron_expression(self, field):
        # Basic CRON validation (5 parts)
        cron_pattern = r'^(\*|[0-5]?\d)\s+(\*|[01]?\d|2[0-3])\s+(\*|[12]?\d|3[01])\s+(\*|[1-9]|1[0-2])\s+(\*|[0-6])$'
        if not re.match(cron_pattern, field.data.strip()):
            raise ValidationError("Ungültiges CRON-Format. Verwenden Sie: Minute Stunde Tag Monat Wochentag")

class GenerateContentForm(FlaskForm):
    topic = StringField("Thema/Briefing", validators=[DataRequired()],
                       description="Beschreiben Sie das gewünschte Thema für den Post")
    
    channel = SelectField("Ziel-Plattform",
                         choices=[("telegram", "Telegram"), ("facebook", "Facebook"),
                                ("linkedin", "LinkedIn"), ("instagram", "Instagram")],
                         validators=[DataRequired()])
    
    generate_image = BooleanField("Bild generieren")
    generate_voice = BooleanField("Sprachausgabe (TTS)")
    
    content_type = SelectField("Content-Typ",
                              choices=[("post", "Standard Post"), ("story", "Story"), ("reel", "Reel/Video")],
                              default="post")
    
    auto_publish = BooleanField("Sofort veröffentlichen", default=False)
    submit = SubmitField("Content generieren")

class UploadFileForm(FlaskForm):
    file = FileField("Datei auswählen", 
                    validators=[DataRequired(), 
                               FileAllowed(['txt', 'pdf', 'docx', 'jpg', 'png', 'mp4', 'mp3'], 
                                         'Nur Text-, Bild-, Audio- und Videodateien erlaubt')])
    
    vector_store_id = StringField("Vector Store ID (optional)", validators=[Optional()],
                                 description="Leer lassen für automatische Zuordnung")
    
    description = TextAreaField("Beschreibung (optional)", validators=[Optional()],
                               description="Beschreibung für die Datei")
    
    submit = SubmitField("Datei hochladen")