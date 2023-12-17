<p align="center">
	<!-- Title -->
	<img src="assets/stremio-logo.png" width="128"/><br>
	<b>🇺🇦 Адонни Stremio</b>
</p>
<p align="center">
<img src="https://img.shields.io/github/languages/code-size/CakesTwix/cloudstream-extensions-uk?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Made_with-Python-099FF0?style=for-the-badge&logo=python"/><br><br>
<a href="https://www.buymeacoffee.com/cakestwix"><img width="150" src="https://img.buymeacoffee.com/button-api/?text=Buy me a tea&emoji=🍵&slug=cakestwix&button_colour=FF5F5F&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00" /></a>
</p>

|                                Іконка                               |  Назва |                Опис                | Версія |                      Маніфест                      |
|:-------------------------------------------------------------------:|:------:|:----------------------------------:|:------:|:--------------------------------------------------:|
| ![Icon](https://www.google.com/s2/favicons?domain=aniage.net&sz=32) | Aniage | Ваше улюблене аніме   українською! |  1.2.0 | https://stremio.cakestwix.com/aniage/manifest.json |

<!-- Brief information about the extension -->
## 📖 Що це таке?
Це API-сервер, написаний на Python для Stremio. Він буде парсити піратські сайти та показувати їх у Stremio.

<!-- Installation guide -->
## ⚙️ Інсталяція адонну
Поки що нема публічного інстансу. :(
```
http://127.0.0.1:8000/manifest.json
```

## 🖥 Selfhost. Як захостити на своєму сервері?
Я тестував тільки на Linux-системі, тобто не можу 100% гарантувати, що воно буде працювати в інших системах, тем паче на Windows.

1. Склонуйте репозиторій.
	```bash
	git clone https://github.com/CakesTwix/stremio-uk
	```

2. Встановлюйте залежності
	```bash
	pip install aiohttp fastapi bs4
	```

3. Запускайте сервер!
	```bash
	cd app; uvicorn stremio:app --reload
	```
- Документація від FastAPI
	```
	http://127.0.0.1:8000/docs
	```
- Маніфест для Stremio
	```
	http://127.0.0.1:8000/manifest.json
	```

<!-- Support -->
## ✅ Підтримка
Для підтримки пишіть в Telegram [@CakesTwix](https://t.me/CakesTwix) або [@cakestwix_talk](https://t.me/cakestwix_talk)

<!-- Contributing -->
## 💖 Зробити внесок
Внески завжди вітаються!

<!-- Developers -->
## ⭐️ Розробники
- [@CakesTwix](https://www.github.com/CakesTwix)
