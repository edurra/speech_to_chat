from flask import render_template, request
from flask import Flask, session
import json
import os
import uuid
import subprocess
import azure.cognitiveservices.speech as speechsdk
app = Flask(__name__)

app.secret_key = os.getenv("FLASK_KEY")
speech_key = os.getenv("SPEECH_KEY")

def speech_recognize_once_from_file(filename):
    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region="westeurope")
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language="en-us", audio_config=audio_config)
    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    result = speech_recognizer.recognize_once()
    # Check the result
    text = None
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        text = result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    # </SpeechRecognitionWithFile>
    return text
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("post received")
        print(request)
        audio_file = request.files['audio_file']
        identif = str(uuid.uuid4())
        file_path = "tmp/" + identif + ".mp3"
        audio_file.save(file_path)
        file_path_wav = "tmp/" + identif + ".wav"
        subprocess.call(["ffmpeg", "-i", file_path, file_path_wav])
        text = speech_recognize_once_from_file(file_path_wav)
        os.remove(file_path)
        os.remove(file_path_wav)
        return json.dumps([{"you": text, "chat": "response"}])
    if request.method == 'GET':
        session["messages"] = []
        return render_template('index.html', title='Welcome')

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0", debug=True)
