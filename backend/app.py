import os
import tempfile
import flask
from flask import request
from flask_cors import CORS
import whisper
from auth_middleware import token_required

app = flask.Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv("MY_SECRET") or 'this is a secret'
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/',methods=['GET'])
def hello():
    if request.method =="GET":
        return 'Hello!'

# endpoint for handling the transcribing of audio inputs

@app.route('/transcribe', methods=['POST', 'GET'])
@token_required
def transcribe():
    print(request.method)
    if request.method == 'POST':
        language = request.form['language']
        model = request.form['model_size']

        # there are no english models for large
        if model != 'large' and language == 'english':
            model = model + '.en'
        audio_model = whisper.load_model(model)

        temp_dir = tempfile.mkdtemp()
        save_path = os.path.join(temp_dir, 'temp.wav')

        wav_file = request.files['audio_data']
        wav_file.save(save_path)

        if language == 'english':
            result = audio_model.transcribe(save_path, language='english')
        else:
            result = audio_model.transcribe(save_path)

        return result['text']
    elif request.method =="GET":
        return "HI"
    else:
        return "This endpoint only processes POST wav blob"
    
if __name__ == '__main__':
    print('Serving Production ... ')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    print('Served')