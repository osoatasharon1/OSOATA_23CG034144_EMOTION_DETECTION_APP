import os
from flask import Flask, render_template, request
import sqlite3
from deepface import DeepFace
import gdown  # make sure gdown is in requirements.txt

app = Flask(__name__)

# Create weights folder if missing
weights_dir = os.path.join(os.path.expanduser("~"), ".deepface/weights")
os.makedirs(weights_dir, exist_ok=True)

# List of model files DeepFace needs
models = {
    "VGG-Face.h5": "YOUR_GOOGLE_DRIVE_LINK_HERE",
    "Facenet.h5": "YOUR_GOOGLE_DRIVE_LINK_HERE",
    # add other weights your app uses
}

# Download models if not present
for file_name, url in models.items():
    path = os.path.join(weights_dir, file_name)
    if not os.path.exists(path):
        gdown.download(url, path, quiet=False)

# Ensure SQLite DB exists
if not os.path.exists("emotion_data.db"):
    conn = sqlite3.connect("emotion_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_path TEXT,
            emotion TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    name = request.form['name']
    image = request.files['file']
    image_path = os.path.join('static', image.filename)
    image.save(image_path)

    result = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    dominant_emotion = result[0]['dominant_emotion']

    conn = sqlite3.connect("emotion_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (name, image_path, emotion) VALUES (?, ?, ?)",
              (name, image_path, dominant_emotion))
    conn.commit()
    conn.close()

    return f"<h2>{name}, your detected emotion is: {dominant_emotion}</h2>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
