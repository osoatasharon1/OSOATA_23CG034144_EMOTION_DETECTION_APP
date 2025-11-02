from flask import Flask, render_template, request
from deepface import DeepFace
import sqlite3
import os

app = Flask(__name__)

# Database setup (create table if not exists)
def init_db():
    conn = sqlite3.connect("emotion_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  image_path TEXT,
                  emotion TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Home route (main page)
@app.route('/')
def home():
    return render_template('index.html')

# Analyze route (when user clicks "Detect Emotion")
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']

        # Save the uploaded image
        image_path = os.path.join('static', image.filename)
        image.save(image_path)

        # Analyze emotion using DeepFace
        from deepface import DeepFace
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'])
        dominant_emotion = result[0]['dominant_emotion']

        # Save to database
        conn = sqlite3.connect("emotion_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name, image_path, emotion) VALUES (?, ?, ?)",
                  (name, image_path, dominant_emotion))
        conn.commit()
        conn.close()

        # Return the result page with data
        return render_template('index.html', name=name, emotion=dominant_emotion, image_path=image_path)

    # If GET request, just show the page
    return render_template('index.html')

if __name__ == '__main__':
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
