# 🌊 Mumbai Explorer — Tourism App

A full-featured Mumbai tourism web app built with Flask + Claude AI.

## Features
- 🔐 **Login / Register** — User authentication system
- 🤖 **AI Chatbot** — Claude-powered Mumbai tourism guide (English + Hinglish)
- 📸 **Snap & Identify** — Upload/camera photo → AI identifies animals, flowers, landmarks, food
- 🗺️ **Interactive Map** — Google Maps embed, navigation, place filtering, download
- 🔭 **360° Virtual Tours** — Street View panoramas of popular places
- 🌟 **Popular Places** — Browse all 10 top Mumbai attractions

## Setup

### 1. Install dependencies
```bash
cd mumbai-tourism
pip install -r requirements.txt
```

### 2. Set your Anthropic API Key
```bash
# Linux/Mac
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows
set ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

## Demo Login
- Username: `demo`  Password: `demo123`
- Username: `tourist`  Password: `mumbai123`

## Project Structure
```
mumbai-tourism/
├── app.py              # Flask backend + API routes
├── requirements.txt    # Dependencies
└── templates/
    ├── base.html       # Navbar + shared layout
    ├── login.html      # Login page
    ├── register.html   # Registration page
    ├── home.html       # Dashboard
    ├── chatbot.html    # AI Guide chatbot
    ├── snap.html       # Snap & Identify
    ├── map.html        # Map & Navigation
    ├── places.html     # Places listing with 360° links
    └── panorama.html   # 360° Virtual Tour viewer
```

## Get Anthropic API Key
Visit: https://console.anthropic.com/
