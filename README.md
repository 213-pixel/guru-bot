# 🤖 Guru Assistant Bot

Bot Telegram untuk membantu administrasi guru dengan AI.

## ✨ Fitur

- 📚 **FAQ Otomatis** - Jawab pertanyaan umum
- 🤖 **AI Chat** - Tanya jawab dengan AI (Groq)
- 📊 **Statistik** - Pantau penggunaan bot
- 📢 **Broadcast** - Kirim pengumuman ke semua user
- 💬 **Feedback** - Terima masukan dari pengguna
- 🔒 **Admin Panel** - Kelola konten via Telegram

## 🚀 Quick Start

1. Clone repo
2. Copy `.env.example` ke `.env` dan isi token
3. Install dependencies: `pip install -r requirements.txt`
4. Set webhook: `python set_webhook.py`
5. Run: `python src/main.py`

## 📦 Deployment

Deploy ke Railway:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

## 🛠️ Tech Stack

- Python 3.11
- aiogram 3.x (Telegram Bot)
- FastAPI (Web Server)
- Groq API (AI)
- SQLite (Database)
- Docker (Deployment)

## 📝 License

MIT