from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask_uploads import UploadSet, configure_uploads, VIDEO
from flask_session import Session
import os
import subprocess

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

videos = UploadSet('videos', VIDEO)
app.config['UPLOADED_VIDEOS_DEST'] = 'uploads'
configure_uploads(app, videos)

def convert_video(input_path, output_path, output_format, resolution):
    command = f'ffmpeg -i {input_path} -vf scale={resolution} {output_path}.{output_format}'
    subprocess.call(command, shell=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'video' in request.files:
        filename = videos.save(request.files['video'])
        session['input_video'] = filename
        return redirect(url_for('convert'))
    return render_template('index.html')


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        output_format = request.form['format']
        resolution = request.form['resolution']
        input_video = session['input_video']
        input_path = f'uploads/{input_video}'
        output_path = f'converted/{input_video}_converted'

        convert_video(input_path, output_path, output_format, resolution)

        session['output_video'] = f'{input_video}_converted.{output_format}'
        return redirect(url_for('download'))
    return render_template('convert.html')


@app.route('/download')
def download():
    output_video = session['output_video']
    return send_from_directory('converted', output_video, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('converted'):
        os.makedirs('converted')
    app.run(debug=True)
