from flask import Flask, render_template, request
from deepface import DeepFace
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

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

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded", 400

    name = request.form['name']
    file = request.files['file']

    if file.filename == '':
        return "No file selected", 400

    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)

    # Analyze emotion
    result = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    dominant_emotion = result[0]['dominant_emotion']

    # Save to database
    conn = sqlite3.connect("emotion_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (name, image_path, emotion) VALUES (?, ?, ?)",
              (name, image_path, dominant_emotion))
    conn.commit()
    conn.close()

    # Send result back to template
    return render_template('index.html', name=name, emotion=dominant_emotion, image_url=image_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
