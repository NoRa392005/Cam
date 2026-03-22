from flask import Flask, request, send_from_directory, render_template_string, jsonify
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Upload route ---
@app.route("/upload", methods=["POST"])
def upload():
    if 'imageFile' not in request.files:
        return "No file", 400

    file = request.files['imageFile']

    # Make filename unique with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    filename = f"{timestamp}_{file.filename}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    print("Saved:", filename)
    return "OK", 200

# --- Serve individual files ---
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# --- API endpoint returning all image filenames ---
@app.route("/api/images")
def api_images():
    images = os.listdir(UPLOAD_FOLDER)
    images = [f for f in images if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    images.sort(reverse=True)  # newest first
    return jsonify(images)

# --- Gallery page with live updates ---
@app.route("/")
def gallery():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Image Gallery</title>
        <style>
            .gallery { display: flex; flex-wrap: wrap; }
            .gallery img { margin: 5px; height: 150px; object-fit: cover; }
        </style>
    </head>
    <body>
        <h1>Live Uploaded Images</h1>
        <div class="gallery" id="gallery"></div>

        <script>
            const gallery = document.getElementById("gallery");
            let loadedImages = new Set();

            async function loadImages() {
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
                        gallery.appendChild(a);

                        loadedImages.add(img);
                    }
                });
            }

            // Initial load
            loadImages();

            // Refresh gallery every 5 seconds
            setInterval(loadImages, 5000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
