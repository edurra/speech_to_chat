
import openai
import azure.cognitiveservices.speech as speechsdk
import os

speech_key = os.getenv("SPEECH_KEY")

openai_key = os.getenv('OPENAI_KEY')
openai.api_key = openai_key

"""
AZURE FUNCTIONS
"""
def speech_recognize_once_from_file(filename):
    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
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
    return text

def text_to_audio(path, text):
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
        pass
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

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
    return interviewer_message


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

def job_interview(position, session_messages, max_messages = 5):
    messages = [
        {"role": "system", "content": f"This is job interview about a {position} job position. You are the interviewer."},
        {"role": "assistant", "content": f"welcome to the job interview for the {position} job position, let's start"},
        {"role": "user", "content": f"hi, nice to meet you, let's start with the interview"}
    ]
    messages = messages + session_messages
    interviewer = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = messages, max_tokens=80)
    interviewer_message = interviewer['choices'][0]['message']['content']
    return interviewer_message
    """
    if len(messages) > max_messages:
        messages = [messages[0]] + messages[len(messages)-max_messages+1:len(messages)]
    """
