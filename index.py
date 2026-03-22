from flask import Flask, request, send_from_directory, render_template_string, jsonify
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if 'imageFile' not in request.files:
        return "No file", 400

    file = request.files['imageFile']
    if file.filename == '':
        return "No filename", 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(filepath)
    return "OK", 200

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/api/images")
def api_images():
    if not os.path.exists(UPLOAD_FOLDER):
        return jsonify([])
    images = os.listdir(UPLOAD_FOLDER)
    images = [f for f in images if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    images.sort(reverse=True)
    return jsonify(images)

@app.route("/")
def gallery():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Satellite Live Gallery</title>
        <style>
            body { font-family: sans-serif; text-align: center; background: #f4f4f4; margin: 0; padding: 20px; }
            .gallery { display: flex; flex-wrap: wrap; justify-content: center; }
            .gallery img { margin: 10px; height: 200px; border: 3px solid #fff; box-shadow: 0 0 5px rgba(0,0,0,0.2); object-fit: cover; border-radius: 8px; }
            h1 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>CubeSat Earth Observation - Live Feed</h1>
        <div class="gallery" id="gallery"></div>
        <script>
            const gallery = document.getElementById("gallery");
            let loadedImages = new Set();
            async function loadImages() {
                try {
                    const response = await fetch("/api/images");
                    const images = await response.json();
                    images.forEach(img => {
                        if (!loadedImages.has(img)) {
                            const a = document.createElement("a");
                            a.href = "/uploads/" + img;
                            a.target = "_blank";
                            const imageElem = document.createElement("img");
                            imageElem.src = "/uploads/" + img;
                            a.appendChild(imageElem);
                            gallery.prepend(a);
                            loadedImages.add(img);
                        }
                    });
                } catch (e) { }
            }
            loadImages();
            setInterval(loadImages, 3000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)
