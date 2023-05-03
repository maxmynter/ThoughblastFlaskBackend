import os
import tempfile
import flask
from flask import request
from flask_cors import CORS
from auth_middleware import token_required
import banana_dev as banana
from pydub import AudioSegment
import base64

app = flask.Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv("MY_SECRET") or 'this is a secret'
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/',methods=['GET'])
def hello():
    print("In root get")
    if request.method =="GET":
        return 'Hello!'

# endpoint for handling the transcribing of audio inputs

@app.route('/transcribe', methods=['POST'])
@token_required
def transcribe():
    if request.method == 'POST':
        print('/transcribe endpoint',request.method)
        wav_file = request.files['audio_data']

        temp_dir = tempfile.mkdtemp()
        save_path = os.path.join(temp_dir, 'temp.wav')
        wav_file.save(save_path)

        recording = AudioSegment.from_wav(save_path)
        mp3_path =os.path.join(temp_dir, 'temp.mp3')
        recording.export(mp3_path, format="mp3")
        print('Saved as, ', mp3_path)
        print(type(recording), type(mp3_path))

        

        with open(mp3_path, 'rb') as f:
            b64_bytes = base64.b64encode(f.read())

        b64_str = b64_bytes.decode('utf-8')
        
        
        banana_inputs = {"mp3BytesString": b64_str}
        print('Off to banana. Transcribing ... ')
        # Run banana
        out = banana.run(os.getenv("BANANA_API_KEY"), os.getenv("BANANA_MODEL_KEY"), banana_inputs)
        print('Banana Output',out)
        transcribed_voice_note = dict(dict(out)['modelOutputs'][0])['text'].strip()

        try: 
            summarise = request.form['summarise'] == 'summarise'
        except:
            summarise = False
        print("Summarise," , summarise)
        if summarise:
            print("Summarising @ OpenAI")
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            prompt =f"You are a a model to summarise, and structure audio transcriptions into clear concise points. Transcript: {transcribed_voice_note}\n Write a tl;dr summary of the transcript. Stay concise. Omit verbose structures. Do not mention the author or medium of publication (Text, Arcticle, etc.). Summary:"
            print('Prompt: ',prompt)
            return_value = openai.Completion.create(
                model="text-curie-001",
                prompt=prompt,
                temperature=1,
                max_tokens=200)
            print("Return Transcribed and Sumarised")
            print(return_value["choices"][0]["text"].strip().strip("/n"))
            return return_value["choices"][0]["text"].strip().strip("/n")

        else:
            print("Return Transcribed")
            return transcribed_voice_note
    
if __name__ == '__main__':
    print('Serving Production ... ')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    print('Served')