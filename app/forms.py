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
        # More flexible CRON validation supporting *, ranges, steps, lists
        # Format: Minute Hour Day Month Weekday
        cron_parts = field.data.strip().split()
        
        if len(cron_parts) != 5:
            raise ValidationError("CRON-Ausdruck muss genau 5 Felder haben: Minute Stunde Tag Monat Wochentag")
        
        # Allow *, numbers, ranges (1-5), steps (*/5), lists (1,2,3)
        cron_field_pattern = r'^(\*|[0-9]+(-[0-9]+)?(,[0-9]+(-[0-9]+)?)*|\*/[0-9]+)$'
        
        for i, part in enumerate(cron_parts):
            if not re.match(cron_field_pattern, part):
                field_names = ["Minute", "Stunde", "Tag", "Monat", "Wochentag"]
                raise ValidationError(f"Ungültiges Format im Feld '{field_names[i]}': {part}")

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