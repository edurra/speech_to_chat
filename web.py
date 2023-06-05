from flask import render_template, request
from flask import Flask, session, Response
import json
import os
import uuid
import subprocess
import openai
import azure.cognitiveservices.speech as speechsdk
app = Flask(__name__)


app.secret_key = os.getenv('FLASK_KEY')

speech_key = os.getenv("SPEECH_KEY")

openai_key = os.getenv('OPENAI_KEY')

openai.api_key = openai_key

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

def text_to_audio(path, text):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region="westeurope")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=path)
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name="en-US-JennyNeural"
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    ssml_text = f'<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-JennyNeural"><mstts:express-as style="chat">{text}</mstts:express-as></voice></speak>'
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_text).get()
    #speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        #print("Speech synthesized for text [{}]".format(text))
        pass
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


def free_talk(session_messages):
    initial_message =  f"This is a conversation between you and the user. Try to make the conversation engaging and ask questions if possible. Give short answers, no more than two sentences."
    messages = [
        {"role": "system",
         "content": initial_message}
    ]
    
    #user_message = recognize_from_microphone()
    #print(f"You: {user_message}")
    #messages.append({"role": "user", "content": user_message})
    messages = messages + session_messages
    assisstant = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=120, temperature = 1)
    assisstant_message = assisstant['choices'][0]['message']['content']
    
    return assisstant_message
    """
    messages.append({"role": "assistant", "content": interviewer_message})
    if len(messages) > max_messages:
        messages = [messages[0]] + messages[len(messages) - max_messages + 1:len(messages)]
    """

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        session["messages"] = []
        session["count"] = 0
        return render_template('index.html', title='Welcome')

@app.route('/chat', methods = ['POST', 'GET'])
def chat(max_messages = 7):
    if request.method == 'POST':
        
        session["count"] += 1
        print("post received")
        print(request)
        audio_file = request.files['audio_file']
        identif = str(uuid.uuid4())
        file_path = "tmp/" + identif + ".mp3"
        audio_file.save(file_path)
        file_path_wav = "tmp/" + identif + ".wav"
        subprocess.run(["ffmpeg", "-i", file_path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        text = speech_recognize_once_from_file(file_path_wav)
        os.remove(file_path)
        os.remove(file_path_wav)
        session["messages"].append({"role": "user", "content": text})
        assistant_response = free_talk(session["messages"])
        session["messages"].append({"role": "assistant", "content": assistant_response})

        if len(session["messages"]) > max_messages:
            print(session["messages"])
            session["messages"] =  session["messages"][len(session["messages"]) - max_messages + 1:len(session["messages"])]
            print(session["messages"])
        
        return json.dumps(session["messages"][len(session["messages"])-2:len(session["messages"])])
        
@app.route('/audio', methods = ['POST', 'GET'])
def audio():
    if request.method == 'GET':
        print("get received")
        print(request)
        print(session["messages"])
        text = session["messages"][len(session["messages"])-1]["content"]
        identif = str(uuid.uuid4())
        file_path = "tmp/" + identif + ".wav"
        #file_path = "tmp/test2.wav"
        text_to_audio(file_path, text)

        response = Response(generate(file_path), mimetype="audio/x-wav")
        
        return response


def generate(path):
    with open(path, "rb") as fwav:
        data = fwav.read(1024)
        while data:
            yield data
            data = fwav.read(1024)

    os.remove(path)


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
