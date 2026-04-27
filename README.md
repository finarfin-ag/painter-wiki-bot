<div align="center">

# 🎨 PainterBot

**A Telegram bot to explore painters and their artworks via Wikimedia Commons**

[

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)

](https://python.org)
[

![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-22.7-blue?style=flat-square)

](https://github.com/python-telegram-bot/python-telegram-bot)
[

![Wikimedia](https://img.shields.io/badge/Powered%20by-Wikimedia-black?style=flat-square&logo=wikipedia)

](https://wikimedia.org)
[

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

](LICENSE)

[English](#english) • [فارسی](#persian)

</div>

---

## English

### What is PainterBot?

PainterBot is a free, open-source Telegram bot that lets you explore painters
and their artworks directly from Wikimedia Commons and Wikidata.
Search any painter by name, read their biography, and browse or download
their works in multiple resolutions — all inside Telegram.

### Features

- 🔍 Search any painter by name (supports typos and fuzzy matching)
- 🌍 Fully bilingual — English and Persian (فارسی)
- 🖼 Browse artworks as thumbnails, paginated 10 at a time
- 🎲 Discover 5 random works from any painter
- 📦 Download paintings in Small / Medium / Large / Original resolution
- 📖 Biographical info: born, died, nationality, movement, portrait
- 🤖 Powered entirely by free Wikimedia APIs — no paid services

### Supported Languages

| Input language | Bot response |
|---|---|
| English (Latin script) | English |
| Persian / Farsi (فارسی) | Persian |

### Getting Started

#### Requirements
- Python 3.10+
- A Telegram Bot token from [@BotFather](https://t.me/botfather)

#### Installation

```bash
git clone https://github.com/finarfin-ag/painter-wiki-bot.git
cd painter-wiki-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
BOT_TOKEN=8704671069:AAFu8mq3jtjXvoBeu2klRvqAyQCNmzlijy8
python3 main.py
cat > ~/painterbot/.env.example << 'EOF'

# Copy this file to .env and add your token

# Get your token from @BotFather on Telegram

BOT_TOKEN=8704671069:AAFu8mq3jtjXvoBeu2klRvqAyQCNmzlijy8

