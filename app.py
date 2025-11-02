from flask import Flask, render_template, request
import os
import sqlite3
from deepface import DeepFace

app = Flask(__name__)

# Ensure static folder exists
if not os.path.exists('static'):
    os.makedirs('static')

# Ensure database exists
conn = sqlite3.connect("emotion_data.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              image_path TEXT,
              emotion TEXT)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    name = request.form.get('name')
    image = request.files.get('file')

    if not name or not image:
        return "Missing name or image!", 400

    # Save the uploaded image
    image_path = os.path.join('static', image.filename)
    image.save(image_path)

    # Analyze emotion using DeepFace
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'])
        dominant_emotion = result[0]['dominant_emotion']
    except Exception as e:
        return f"Error analyzing image: {str(e)}", 500

    # Save to database
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
