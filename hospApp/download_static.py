import urllib.request
import os

# Create folders
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/fonts/poppins', exist_ok=True)

print("Downloading Bootstrap CSS...")
urllib.request.urlretrieve(
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'static/css/bootstrap.min.css'
)

print("Downloading Bootstrap JS...")
urllib.request.urlretrieve(
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    'static/js/bootstrap.bundle.min.js'
)

print("All files downloaded successfully!")