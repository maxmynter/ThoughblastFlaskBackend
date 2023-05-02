import os
import tempfile
import flask
from flask import request
from flask_cors import CORS
import whisper
import torch 
from auth_middleware import token_required

app = flask.Flask(__name__)
CORS(app)
torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

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
    print('/transcribe endpoint',request.method)
    print(request.form)
    if request.method == 'POST':
        language = request.form['language']
        model = request.form['model_size']
        try: 
            summarise = request.form['summarise'] == 'summarise'
        except:
            summarise = False

        # there are no english models for large
        print("Selecting model")
        if model != 'large' and language == 'english':
            model = model + '.en'
        audio_model = whisper.load_model(model, device=DEVICE)
        print('Run model on device:', DEVICE)


        temp_dir = tempfile.mkdtemp()
        save_path = os.path.join(temp_dir, 'temp.wav')

        wav_file = request.files['audio_data']
        wav_file.save(save_path)

        print('Transcribing ... ')
        if language == 'english':
            result = audio_model.transcribe(save_path, language='english')
        else:
            result = audio_model.transcribe(save_path)

        print('Finished Transcription')

        if summarise:
            print("Summarising @ OpenAI")
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            prompt =f"You are a a model to summarise, and structure audio transcriptions into clear concise points. Transcript: {result['text']}\n Write a tl;dr summary of the Input. Stay concise. Write bullets and notes, not full sentences. Omit verbose structures. Do not mention the author or medium of publication (Text, Arcticle, etc.) tl;dr summary of transcript:"
            return_value = openai.Completion.create(
                model="text-curie-001",
                prompt=prompt,
                temperature=1,
                max_tokens=200)
            print("Return Transcribed and Sumarised")
            return return_value["choices"][0]["text"].strip().strip("/n")

        else:
            print("Return Transcribed")
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