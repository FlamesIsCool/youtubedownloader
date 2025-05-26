from flask import Flask, render_template, request, send_file
from pytube import YouTube
import os
from moviepy.editor import AudioFileClip

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_choice = request.form['format']
    yt = YouTube(url)
    title = yt.title.replace(" ", "_").replace("/", "_")

    if format_choice == 'mp4':
        stream = yt.streams.get_highest_resolution()
        file_path = stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{title}.mp4")
    else:
        stream = yt.streams.filter(only_audio=True).first()
        audio_path = stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{title}.mp4")
        mp3_path = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp3")
        AudioFileClip(audio_path).write_audiofile(mp3_path)
        os.remove(audio_path)
        file_path = mp3_path

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
