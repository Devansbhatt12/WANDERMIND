from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import base64, os, json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
app.secret_key = "mumbai_tourism_secret_2024"

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE"))

# ─── In-memory user store ────────────────────────────────────────────────────
USERS = {
    "demo": {"password": "demo123", "name": "Demo User"},
    "tourist": {"password": "mumbai123", "name": "Mumbai Explorer"},
}

MUMBAI_PLACES = [
    {"id": 1, "name": "Gateway of India",     "lat": 18.9220, "lng": 72.8347, "category": "Monument",  "rating": 4.7, "desc": "Iconic arch monument built during British Raj era, overlooking the Arabian Sea.", "img": "gateway"},
    {"id": 2, "name": "Marine Drive",          "lat": 18.9432, "lng": 72.8232, "category": "Landmark",  "rating": 4.8, "desc": "The Queen's Necklace — a 3.6 km long boulevard along the Arabian Sea coast.", "img": "marine"},
    {"id": 3, "name": "Elephanta Caves",       "lat": 18.9633, "lng": 72.9315, "category": "Heritage",  "rating": 4.5, "desc": "UNESCO World Heritage site with rock-cut caves dedicated to Lord Shiva.", "img": "elephanta"},
    {"id": 4, "name": "Chhatrapati Shivaji Terminus", "lat": 18.9398, "lng": 72.8355, "category": "Heritage", "rating": 4.6, "desc": "UNESCO-listed Victorian Gothic railway station, architectural masterpiece.", "img": "cst"},
    {"id": 5, "name": "Juhu Beach",            "lat": 19.0948, "lng": 72.8258, "category": "Beach",     "rating": 4.3, "desc": "Famous beach known for street food, sunsets and Bollywood celebrity sightings.", "img": "juhu"},
    {"id": 6, "name": "Haji Ali Dargah",       "lat": 18.9827, "lng": 72.8090, "category": "Religious", "rating": 4.6, "desc": "15th-century mosque and dargah located on a tiny islet in the Arabian Sea.", "img": "hajiali"},
    {"id": 7, "name": "Siddhivinayak Temple",  "lat": 19.0168, "lng": 72.8301, "category": "Religious", "rating": 4.7, "desc": "One of Mumbai's most famous temples dedicated to Lord Ganesha.", "img": "siddhivinayak"},
    {"id": 8, "name": "Colaba Causeway",       "lat": 18.9143, "lng": 72.8302, "category": "Shopping",  "rating": 4.4, "desc": "Vibrant street market with antiques, clothes, jewellery and street food.", "img": "colaba"},
    {"id": 9, "name": "Dharavi",               "lat": 19.0417, "lng": 72.8530, "category": "Cultural",  "rating": 4.2, "desc": "Asia's largest slum turned cultural hub with thriving small industries.", "img": "dharavi"},
    {"id":10, "name": "Bandra-Worli Sea Link", "lat": 19.0176, "lng": 72.8169, "category": "Landmark",  "rating": 4.9, "desc": "8-lane cable-stayed bridge spanning 5.6 km over Mahim Bay.", "img": "sealink"},
]

PANORAMA_URLS = {
    "Gateway of India":     "https://www.google.com/maps/embed?pb=!4v1716000000000!6m8!1m7!1sCAoSLEFGMVFpcE1fMW5vZU1ZV1hTSVJlOG1uNWFrSmhBbS1VZVgzSWdnMWZkWjU!2m2!1d18.9220!2d72.8347!3f0!4f0!5f0.7820865814881103",
    "Marine Drive":         "https://www.google.com/maps/embed?pb=!4v1716000000001!6m8!1m7!1sCAoSLEFGMVFpcE1fMW5vZU1ZV1hTSVJlOG1uNWFrSmhBbS1VZVgzSWdnMWZkWjU!2m2!1d18.9432!2d72.8232!3f90!4f0!5f0.7820865814881103",
    "Elephanta Caves":      "https://www.google.com/maps/embed?pb=!4v1716000000002!6m8!1m7!1sCAoSLEFGMVFpcE1fMW5vZU1ZV1hTSVJlOG1uNWFrSmhBbS1VZVgzSWdnMWZkWjU!2m2!1d18.9633!2d72.9315!3f180!4f0!5f0.7820865814881103",
    "Chhatrapati Shivaji Terminus": "https://www.google.com/maps/embed?pb=!4v1716000000003!6m8!1m7!1sCAoSLEFGMVFpcE1fMW5vZU1ZV1hTSVJlOG1uNWFrSmhBbS1VZVgzSWdnMWZkWjU!2m2!1d18.9398!2d72.8355!3f270!4f0!5f0.7820865814881103",
    "Bandra-Worli Sea Link":"https://www.google.com/maps/embed?pb=!4v1716000000010!6m8!1m7!1sCAoSLEFGMVFpcE1fMW5vZU1ZV1hTSVJlOG1uNWFrSmhBbS1VZVgzSWdnMWZkWjU!2m2!1d19.0176!2d72.8169!3f45!4f0!5f0.7820865814881103",
}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── Auth routes ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("home"))

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            session["name"] = USERS[username]["name"]
            return redirect(url_for("home"))
        error = "Invalid credentials. Try demo / demo123"
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET","POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        name     = request.form.get("name","").strip()
        if username in USERS:
            error = "Username already exists!"
        elif len(username) < 3:
            error = "Username must be at least 3 characters."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            USERS[username] = {"password": password, "name": name}
            session["user"] = username
            session["name"] = name
            return redirect(url_for("home"))
    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─── Main pages ───────────────────────────────────────────────────────────────
@app.route("/home")
@login_required
def home():
    return render_template("home.html", name=session.get("name"), places=MUMBAI_PLACES)

@app.route("/chatbot")
@login_required
def chatbot():
    return render_template("chatbot.html", name=session.get("name"))

@app.route("/snap")
@login_required
def snap():
    return render_template("snap.html", name=session.get("name"))

@app.route("/map")
@login_required
def map_page():
    return render_template("map.html", name=session.get("name"), places=json.dumps(MUMBAI_PLACES))

@app.route("/places")
@login_required
def places():
    return render_template("places.html", name=session.get("name"), places=MUMBAI_PLACES)

@app.route("/panorama/<place_name>")
@login_required
def panorama(place_name):
    url = PANORAMA_URLS.get(place_name)
    return render_template("panorama.html", name=session.get("name"), place=place_name, panorama_url=url)

# ─── API endpoints ────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data     = request.json
    messages = data.get("messages", [])
    user_msg = data.get("message", "")

    system_prompt = """You are MumbaiGuide AI — an expert, friendly tourism assistant for Mumbai, India.
You help tourists explore Mumbai by answering questions about:
- Famous places: Gateway of India, Marine Drive, Elephanta Caves, CST, Juhu Beach, Haji Ali, Siddhivinayak, Dharavi, Sea Link, Colaba Causeway
- Best food spots: Vada Pav, Pav Bhaji, Bhel Puri, seafood restaurants, Irani cafes, street food
- Getting around: Local trains, Metro, BEST buses, auto-rickshaws, taxis, ferries
- Practical tips: Best time to visit, weather, safety, costs, Mumbai etiquette
- Culture: Bollywood, festivals like Ganesh Chaturthi, local customs
- Nightlife, shopping, hidden gems

Always respond in the same language the user writes in (English or Hindi/Hinglish).
Be enthusiastic, knowledgeable, and give practical, actionable advice.
Keep responses concise but informative. Use emojis occasionally to be friendly. 🌊"""

    api_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        api_messages.append({"role": m["role"], "content": m["content"]})
    api_messages.append({"role": "user", "content": user_msg})

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            max_tokens=800,
        )
        return jsonify({"reply": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/api/snap", methods=["POST"])
@login_required
def api_snap():
    data = request.json
    image_b64 = data.get("image","")
    if image_b64.startswith("data:"):
        header, image_b64 = image_b64.split(",", 1)
        media_type = header.split(";")[0].split(":")[1]
    else:
        media_type = "image/jpeg"

    snap_prompt = """You are a nature & place identifier for Mumbai tourism app.
Identify what's in this image. Focus on:
1. If it's an ANIMAL: species name, habitat, whether it's common in Mumbai/Maharashtra, interesting facts, conservation status
2. If it's a FLOWER/PLANT: species name, local name, medicinal uses, where found in Mumbai
3. If it's a MUMBAI PLACE/LANDMARK: name it, history, visiting tips, timings, entry fee
4. If it's FOOD: dish name, where to find it in Mumbai, price range

Format your response with:
🔍 **Identified:** [name]
📍 **Found in Mumbai:** [yes/no + where]
📖 **About:** [2-3 sentences]
💡 **Fun Fact:** [one interesting fact]
🗺️ **Tip:** [visitor/tourist tip if applicable]"""

    try:
        resp = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_b64}"}},
                    {"type": "text", "text": snap_prompt}
                ]
            }],
            max_tokens=600,
        )
        return jsonify({"result": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"result": f"Error identifying image: {str(e)}"}), 500

@app.route("/api/places")
@login_required
def api_places():
    return jsonify(MUMBAI_PLACES)

if __name__ == "__main__":
    app.run(debug=True, port=5000)