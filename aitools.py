import openai
import azure.cognitiveservices.speech as speechsdk
import os
import utils
import subprocess
from gtts import gTTS
import tiktoken
import whisper

model = whisper.load_model("base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

speech_key = os.getenv("SPEECH_KEY")

openai_key = os.getenv('OPENAI_KEY')
openai.api_key = openai_key

"""
HELPERS
"""
def count_tokens(messages):
    n = 0
    for message in messages:
        text = message["content"]
        n += len(encoding.encode(text))
    return n

"""
AZURE FUNCTIONS
"""
def speech_recognize_once_from_file(filename):
    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
    """
    name = filename.split(".") 

    #subprocess.run(["ffmpeg", "-i", filename, "-af", "volume=7", "-vcodec", "copy", name[0]+"vol"+"."+name[1]], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region="westeurope")
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language="en-US", audio_config=audio_config)
    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    result = speech_recognizer.recognize_once()
    # Check the result
    text = None
    duration = utils.get_wav_duration(filename)
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        #print("Recognized: {}".format(result.text))
        text = result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    # </SpeechRecognitionWithFile>
    """
    name = filename.split(".")[0]
    file_path_wav = name + ".wav"
    result = model.transcribe(filename)
    text = result["text"]
    duration = utils.get_wav_duration(file_path_wav)
    return text, duration

def text_to_audio(path, text):
    """
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region="westeurope")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=path)
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name="en-US-JennyNeural"
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    #ssml_text = f'<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="es-ES"><voice name="es-ES-DarioNeural"><mstts:express-as style="chat">{text}</mstts:express-as></voice></speak>'

    ssml_text = f'<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-JennyNeural"><mstts:express-as style="chat">{text}</mstts:express-as></voice></speak>'
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_text).get()
    #speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        #print("Speech synthesized for text [{}]".format(text))
        duration = utils.get_wav_duration(path)
        return duration
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
    """
    ob=gTTS(text=text, lang='en', slow=False)
    ob.save(path)


"""
OPENAI FUNCTIONS
"""
def random_topic():
    initial_message =  f"This is a conversation about a random topic. You are the one that will suggest the topic to discuss about."
    messages = [
        {"role": "system",
         "content": initial_message},
        {"role": "user",
         "content": f"Hi! which topic do you want to discuss about?"}
    ]
    
    interviewer = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=70, temperature = 1.4)
    interviewer_message = interviewer['choices'][0]['message']['content']

    messages += [{"role": "assistant", "content": interviewer_message}]
    n_tokens = interviewer["usage"]["total_tokens"]

    return interviewer_message, n_tokens


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

    messages += [{"role": "assistant", "content": assisstant_message}]
    n_tokens = assisstant["usage"]["total_tokens"]
    
    return assisstant_message, n_tokens
    """
    messages.append({"role": "assistant", "content": interviewer_message})
    if len(messages) > max_messages:
        messages = [messages[0]] + messages[len(messages) - max_messages + 1:len(messages)]
    """

def job_interview(position, session_messages):
    messages = [
        {"role": "system", "content": f"This is job interview about a {position} job position. You are the interviewer."},
        {"role": "assistant", "content": f"welcome to the job interview for the {position} job position, let's start"},
        {"role": "user", "content": f"hi, nice to meet you, let's start with the interview"}
    ]
    if len(session_messages) > 0:
        messages = [messages[0]] + session_messages
    interviewer = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = messages, max_tokens=80)
    interviewer_message = interviewer['choices'][0]['message']['content']
    messages += [{"role": "assistant", "content": interviewer_message}]
    n_tokens = interviewer["usage"]["total_tokens"]
    return interviewer_message, n_tokens
    """
    if len(messages) > max_messages:
        messages = [messages[0]] + messages[len(messages)-max_messages+1:len(messages)]
    """

def debate(session_messages):
    messages = [
        {"role": "system", "content": f"This is a debate between you an the user. You have to suggest the topic, prefereable a controversial one. You have to disagree with the user"},
        {"role": "assistant", "content": f"welcome to the debate, let's start"},
        {"role": "user", "content": f"what topic do you want to debate about?"}
    ]
    if len(session_messages) > 0:
        messages = [messages[0]] + session_messages
    interviewer = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = messages, max_tokens=90)
    interviewer_message = interviewer['choices'][0]['message']['content']

    messages += [{"role": "assistant", "content": interviewer_message}]
    n_tokens = interviewer["usage"]["total_tokens"]
    return interviewer_message, n_tokens

def suggestion(text):
    initial_message =  f"Give feedback about how natural a sentence is. If it is not natural, suggest one or two alternatives. Give short responses."
    messages = [
        {"role": "system",
         "content": initial_message},
        {"role": "user",
         "content": f"The text to evaluate is: '{text}'"}
    ]
    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=70, temperature = 1)
    suggestion = response['choices'][0]['message']['content']

    n_tokens = response["usage"]["total_tokens"]

    return suggestion, n_tokens

def random_word():
    initial_message =  f"Give just a random word or idiom."
    messages = [
        {"role": "system",
         "content": initial_message}
    ]
    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=70, temperature = 1.5)
    word = response['choices'][0]['message']['content']

    n_tokens = response["usage"]["total_tokens"]

    return word, n_tokens

def random_word_feedback(word, text):
    initial_message =  f"Give feedback about good the description of the word or idiom '{word}' is and describe it if it is not good. Give short answers"
    messages = [
        {"role": "system",
         "content": initial_message},
        {"role": "user",
         "content": f"{text}"}
    ]
    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=70, temperature = 1)
    suggestion = response['choices'][0]['message']['content']

    n_tokens = response["usage"]["total_tokens"]

    return suggestion, n_tokens