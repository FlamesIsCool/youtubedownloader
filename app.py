from flask import Flask, render_template, request, send_file
from pytube import YouTube
import os
import subprocess
import re

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        format_choice = request.form['format']
        print(f"[INFO] Download requested: {url} as {format_choice}")

        yt = YouTube(url)
        title = re.sub(r'[\\/*?:"<>|]', "", yt.title)  # sanitize filename
        print(f"[INFO] Video title: {title}")

        if format_choice == 'mp4':
            stream = yt.streams.get_highest_resolution()
            file_path = stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{title}.mp4")
        else:
            stream = yt.streams.filter(only_audio=True).first()
            audio_path = stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{title}.mp4")
            mp3_path = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp3")

            print(f"[INFO] Running ffmpeg...")
            result = subprocess.run(['ffmpeg', '-y', '-i', audio_path, mp3_path], capture_output=True, text=True)
            if result.returncode != 0:
                print("[ERROR] ffmpeg failed:", result.stderr)
                return "ffmpeg conversion failed", 500

            os.remove(audio_path)
            file_path = mp3_path

        print(f"[INFO] File ready: {file_path}")
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        print("[ERROR] Exception occurred:", str(e))
        return "Internal Server Error", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
