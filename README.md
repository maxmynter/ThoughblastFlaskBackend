# Thought Blast Backend

Hi, I was developing [Thought Blast](https://github.com/maxmynter/thoughblast) during the Nights&Weekends bootcamp by [buildspace](https://buildspace.so/).

The goal was to develop and ship an app and incorporate user feedback to  make it better.

This is the backend and mainly used to convert the .wav files from iOS devices to base64 mp3 bytestrings used as the input to a serverless GPU hosted by [banana.dev](https://www.banana.dev/) whicht houses the open source speech-to-text model whisper.

For longer voice notes, I also use openAI's api to GPT-3 to summarise the voice notes. 

I deployed this using [railway](railway.app)

### Technologies
- Flask
- REST APIs
- En-& decryption using JWT
- Docker






