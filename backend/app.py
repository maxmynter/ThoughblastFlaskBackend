import os
import tempfile
import flask
from flask import request
from flask_cors import CORS
from auth_middleware import token_required
import banana_dev as banana
from pydub import AudioSegment
import base64
from dotenv import load_dotenv

load_dotenv()

app = flask.Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv("MY_SECRET") or 'this is a secret'
app.config['SECRET_KEY'] = os.getenv("MY_SECRET")
app.config['PORT'] = os.getenv("PORT", 5000)
app.config['BANANA_MODEL_KEY'] = os.getenv("BANANA_MODEL_KEY")


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
        try:
            out = banana.run(os.getenv("BANANA_API_KEY"), os.getenv("BANANA_MODEL_KEY"), banana_inputs)
        except:
            return "Failed Request to Banana", 503
        print('Banana Output',out)
        transcribed_voice_note = dict(dict(out)['modelOutputs'][0])['text'].strip()

        try: 
            summarise_flag_set = request.form['summarise'] == 'summarise'
            recording_long_enough = recording.duration_seconds > 20
            print('Summarising Flag', summarise_flag_set, 'Length Flag', recording_long_enough, "Recording Length", recording.duration_seconds)
            summarise = summarise_flag_set and recording_long_enough
        except:
            summarise = False
        print("Summarise," , summarise)
        if summarise:
            try:
                print("Summarising @ OpenAI")
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY")
                prompt =f"You are a model to summarise, and structure audio transcriptions of your thoughts into clear concise points. The thoughts you had are already transcribed and will be provided below this instructions. Write a tl;dr summary of the transcript. Stay concise. Omit verbose structures. You are the author of the thoughts. So dont mention 'the author' etc., rather refer to I, me, etc.  Do not mention the medium (transcript, voice recording, article). Do not omit vital information.\n\nTranscript: {transcribed_voice_note}\n\nSummary:"
                print('Prompt: ',prompt)
                return_value = openai.Completion.create(
                    model="text-curie-001",
                    prompt=prompt,
                    temperature=1,
                    max_tokens=200)
                print("Return Transcribed and Sumarised")
                print(return_value["choices"][0]["text"].strip().strip("/n"))
                return return_value["choices"][0]["text"].strip().strip("/n")
            except:
                print('Failed request to openAI')
                return transcribed_voice_note

        else:
            print("Return Transcribed")
            return transcribed_voice_note
    

## Testing Routes 
@app.route('/',methods=['GET'])
def hello():
    print("In root get")
    if request.method =="GET":
        return 'Hello!'

@app.route('/testencryption',methods=['GET'])
@token_required
def test_encryption():
    print("In testencryption get")
    if request.method =="GET":
        return 'Hello! Encryption seems to work'



if __name__ == '__main__':
    with app.app_context():
        print('Serving Production ... ')
        port = flask.current_app.config["PORT"]
        print('Port: ', port)
        from waitress import serve
        serve(app, host="0.0.0.0", port=port) 
        print('Served')