# Open Graph Image Guide

## Створення og-default.jpg

Вам потрібно створити файл `app/static/img/og-default.jpg` з наступними параметрами:

### Технічні вимоги:
- **Розмір**: 1200x630 пікселів (рекомендований Facebook/LinkedIn)
- **Формат**: JPEG (або PNG)
- **Розмір файлу**: < 8 MB (рекомендовано < 1 MB)
- **Співвідношення сторін**: 1.91:1

### Рекомендації щодо дизайну:
1. **Текст**: Розміщуйте текст у центральній зоні (safe zone)
2. **Логотип**: У верхньому лівому або центрі
3. **Фон**: Яскравий, але не занадто контрастний
4. **Шрифти**: Великі, читабельні

### Приклади контенту для зображення:
```
┌─────────────────────────────────────────┐
│   🤖 Marketing Agent                    │
│                                         │
│   KI-gestützte Marketing Automation    │
│                                         │
│   ✓ Telegram  ✓ LinkedIn               │
│   ✓ Facebook  ✓ Instagram               │
│                                         │
│        Andrii-IT                        │
└─────────────────────────────────────────┘
```

### Інструменти для створення:
- **Canva**: https://www.canva.com/ (шаблон Open Graph)
- **Figma**: https://www.figma.com/
- **Adobe Photoshop/Illustrator**
- **GIMP** (безкоштовний)

### Альтернатива - використати існуюче зображення:
Якщо у вас вже є лого або банер, можете використати його.

### Після створення:
1. Збережіть як `og-default.jpg` у `app/static/img/`
2. Або використайте абсолютний URL через ENV:
   ```
   OG_IMAGE_ABS=https://your-cdn.com/marketing-agent-og.jpg
   ```

### Також створіть favicon:
Файл `app/static/img/favicon.png` (32x32 або 64x64 пікселів)

### Тестування Open Graph:
Після розміщення зображення перевірте на:
- **Facebook Sharing Debugger**: https://developers.facebook.com/tools/debug/
- **LinkedIn Post Inspector**: https://www.linkedin.com/post-inspector/
- **Twitter Card Validator**: https://cards-dev.twitter.com/validator

Введіть URL вашого сайту (наприклад: https://marketing-agent-p4ig.onrender.com) і переконайтесь, що зображення відображається коректно.
