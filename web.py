from flask import render_template, request, redirect
from flask import Flask, session, Response, url_for
import json
import os
import uuid
import requests
import subprocess
import aitools
import dbutils
import utils
from authlib.integrations.flask_client import OAuth
from functools import wraps


app = Flask(__name__)
oauth = OAuth(app)


app.secret_key = str(uuid.uuid4())


google_id = os.getenv('GOOGLE_ID')

google_secret = os.getenv('GOOGLE_SECRET')


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    client_id=google_id,
    client_secret=google_secret,
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

"""
HELPERS AND DECORATORS
"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("google_token") is None or not validate_token(session.get("google_token").get("access_token")):
            return redirect(url_for('home', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def payment_required(f):
    @wraps(f)
    def decorated_function_payment(*args, **kwargs):
        if not validate_payment(session.get("google_token").get("userinfo").get("email")):
            return redirect(url_for('profile', next=request.url))
        return f(*args, **kwargs)
    return decorated_function_payment

def validate_token(token):
    if token == None:
        return False
    else:
        r = requests.get(CONF_URL)
        userinfo_endpoint = r.json()["userinfo_endpoint"]
        user_req = requests.get(userinfo_endpoint, headers = {"Authorization": "Bearer " + token})
        if user_req.status_code == 200:
            return True
        else:
            return False

def validate_payment(email):
    seconds_consumed = dbutils.get_seconds(email)
    seconds_purchased = dbutils.get_purchased_seconds(email)
    return seconds_purchased > seconds_consumed

def generate(path):
    with open(path, "rb") as fwav:
        data = fwav.read(1024)
        while data:
            yield data
            data = fwav.read(1024)

    os.remove(path)



"""
ROUTES
"""

@app.route('/free', methods = ['POST', 'GET'])
@login_required
@payment_required
def free():
    if request.method == 'GET':
        session["messages"] = []
        session["count"] = 0
        return render_template('index.html', title='Welcome', mode="Free Chat Mode", username=session["google_token"]["userinfo"]["given_name"])

@app.route('/chat', methods = ['POST', 'GET'])
@login_required
@payment_required
def chat(max_messages = 7):
    if request.method == 'POST':
        
        session["count"] += 1
        
        audio_file = request.files['audio_file']
        identif = str(uuid.uuid4())
        file_path = "tmp/" + identif + ".mp3"
        audio_file.save(file_path)
        file_path_wav = "tmp/" + identif + ".wav"
        subprocess.run(["ffmpeg", "-i", file_path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        text, duration = aitools.speech_recognize_once_from_file(file_path)
        dbutils.update_seconds(session["google_token"]["userinfo"]["email"], duration)
        os.remove(file_path)
        os.remove(file_path_wav)
        session["messages"].append({"role": "user", "content": text})

        assistant_response, used_tokens = aitools.free_talk(session["messages"])
        dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)

        session["messages"].append({"role": "assistant", "content": assistant_response})

        if len(session["messages"]) > max_messages:
            session["messages"] =  session["messages"][len(session["messages"]) - max_messages + 1:len(session["messages"])]
        
        suggestion, sug_tokens = aitools.suggestion(text)

        response = {"messages": session["messages"][len(session["messages"])-2:len(session["messages"])], "suggestion": suggestion}
        return json.dumps(response)
        #return json.dumps([{"a": "b"}])

@app.route('/random', methods = ['POST', 'GET'])
@login_required
@payment_required
def random():
    if request.method == 'POST':
        
        session["count"] += 1

        assistant_message, used_tokens = aitools.random_topic()
        dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
        session["messages"].append({"role": "assistant", "content": assistant_message})

        return json.dumps({"messages": session["messages"], "suggestion": ""})
        
        #return {"messages": [{"a":"b"}], "sugestion": "aaabbb"}
    if request.method == 'GET':
        
        session["messages"] = []
        session["count"] = 0
        return render_template('random.html', title='Welcome', mode="Random Topic Mode", username=session["google_token"]["userinfo"]["given_name"])

@app.route('/vocabulary_word', methods = ['POST', 'GET'])
@app.route('/vocabulary_feedback', methods = ['POST', 'GET'])
@login_required
@payment_required
def vocabulary():
    if request.method == 'POST':
        if request.path == "/vocabulary_word":
            session["count"] += 1

            assistant_message, used_tokens= aitools.random_word()
            dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
            
            session["word"] = assistant_message
            session["messages"] = [{"role": "assistant", "content": assistant_message}]
            return json.dumps({"messages": [{"role": "assistant", "content": assistant_message}], "suggestion": ""})
        

        if request.path == "/vocabulary_feedback":
            session["count"] += 1
            audio_file = request.files['audio_file']
            identif = str(uuid.uuid4())
            file_path = "tmp/" + identif + ".mp3"
            audio_file.save(file_path)
            file_path_wav = "tmp/" + identif + ".wav"
            subprocess.run(["ffmpeg", "-i", file_path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            text, duration = aitools.speech_recognize_once_from_file(file_path)
            dbutils.update_seconds(session["google_token"]["userinfo"]["email"], duration)
            os.remove(file_path)
            os.remove(file_path_wav)
            #os.remove(identif+"vol.wav")
            """
            new_word, used_tokens = aitools.random_word()

            dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
            """
            suggestion, sug_tokens = aitools.random_word_feedback(session["word"], text)
            messages = [{"role": "user", "content": text}]
            """
            messages = [{"role": "user", "content": text}, {"role": "assistant", "content": new_word}]
            session["word"] = new_word
            session["messages"] = [{"role": "assistant", "content": new_word}]
            """
            response = {"messages": messages, "suggestion": suggestion}
            return json.dumps(response)
        #return [{"a":"b"}]
    if request.method == 'GET':
        
        session["messages"] = []
        session["word"] = ""
        session["count"] = 0
        return render_template('random_word.html', title='Welcome', mode="Debate Mode", username=session["google_token"]["userinfo"]["given_name"])

@app.route('/debate', methods = ['POST', 'GET'])
@app.route('/debate_init', methods = ['POST', 'GET'])
@login_required
@payment_required
def debate(max_messages=7):
    if request.method == 'POST':
        if request.path == "/debate_init":
            session["count"] += 1

            assistant_message, used_tokens= aitools.debate(session["messages"])
            dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
            session["messages"].append({"role": "assistant", "content": assistant_message})
            return json.dumps({"messages": session["messages"], "suggestion": ""})
        

        if request.path == "/debate":
            session["count"] += 1
            audio_file = request.files['audio_file']
            identif = str(uuid.uuid4())
            file_path = "tmp/" + identif + ".mp3"
            audio_file.save(file_path)
            file_path_wav = "tmp/" + identif + ".wav"
            subprocess.run(["ffmpeg", "-i", file_path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            text, duration = aitools.speech_recognize_once_from_file(file_path)
            dbutils.update_seconds(session["google_token"]["userinfo"]["email"], duration)
            os.remove(file_path)
            os.remove(file_path_wav)
            #os.remove(identif+"vol"+".wav")
            session["messages"].append({"role": "user", "content": text})
            assistant_response, used_tokens = aitools.debate(session["messages"])
            dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
            session["messages"].append({"role": "assistant", "content": assistant_response})
            if len(session["messages"]) > max_messages:
                session["messages"] =  session["messages"][len(session["messages"]) - max_messages + 1:len(session["messages"])]
            
            suggestion, sug_tokens = aitools.suggestion(text)

            response = {"messages": session["messages"][len(session["messages"])-2:len(session["messages"])], "suggestion": suggestion}
            return json.dumps(response)
        #return [{"a":"b"}]
    if request.method == 'GET':
        
        session["messages"] = []
        session["count"] = 0
        return render_template('debate.html', title='Welcome', mode="Debate Mode", username=session["google_token"]["userinfo"]["given_name"])

@app.route('/job_interview', methods = ['POST', 'GET'])
@app.route('/job_interview_init', methods = ['POST', 'GET'])
@login_required
@payment_required
def job_interview(max_messages=7):
    if request.method == 'POST':
        """
        session["count"] += 1
        print("get received")
        print(request)
        assistant_message = aitools.random_topic()
        session["messages"].append({"role": "assistant", "content": assistant_message})

        
        return json.dumps(session["messages"])
        """
        if request.path == "/job_interview_init":
            job_position = request.json["job_position"]
            session["job_position"] = job_position
            session["count"] += 1

            interviewer_message, used_tokens = aitools.job_interview(job_position, session["messages"])
            dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
            session["messages"].append({"role": "assistant", "content": interviewer_message})
            return json.dumps({"messages": session["messages"], "suggestion": ""})
        
        if request.path == "/job_interview":
            session["count"] += 1

            
            audio_file = request.files['audio_file']
            identif = str(uuid.uuid4())
            file_path = "tmp/" + identif + ".mp3"
            audio_file.save(file_path)
            file_path_wav = "tmp/" + identif + ".wav"
            subprocess.run(["ffmpeg", "-i", file_path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            text, duration = aitools.speech_recognize_once_from_file(file_path)
            dbutils.update_seconds(session["google_token"]["userinfo"]["email"], duration)

            os.remove(file_path)
            os.remove(file_path_wav)
            #os.remove(identif+"vol.wav")
            session["messages"].append({"role": "user", "content": text})
            assistant_response, used_tokens = aitools.job_interview(session["job_position"], session["messages"])
            dbutils.update_tokens(session["google_token"]["userinfo"]["email"], used_tokens)
            session["messages"].append({"role": "assistant", "content": assistant_response})

            if len(session["messages"]) > max_messages:
                session["messages"] =  session["messages"][len(session["messages"]) - max_messages + 1:len(session["messages"])]
        
            suggestion, sug_tokens = aitools.suggestion(text)

            response = {"messages": session["messages"][len(session["messages"])-2:len(session["messages"])], "suggestion": suggestion}
            return json.dumps(response)

    if request.method == 'GET':
        session["job_position"] = ""
        session["messages"] = []
        session["count"] = 0
        return render_template('jobinterview.html', title='Welcome', mode="Job Interview Mode", username=session["google_token"]["userinfo"]["given_name"])


@app.route('/home', methods = ['POST', 'GET'])
@app.route('/', methods = ['POST', 'GET'])
def home():

    if request.method == 'GET':
        
        return render_template('home.html', title='Welcome')                

        
@app.route('/audio', methods = ['POST', 'GET'])
@app.route('/audio_random', methods = ['POST', 'GET'])
@app.route('/audio_job', methods = ['POST', 'GET'])
@app.route('/audio_debate', methods = ['POST', 'GET'])
@app.route('/audio_vocabulary', methods = ['POST', 'GET'])
@login_required
@payment_required
def audio():
    if request.method == 'GET':

        #print(session["messages"])
        text = session["messages"][len(session["messages"])-1]["content"]
        identif = str(uuid.uuid4())
        file_path_wav = "tmp/" + identif + ".wav"
        #file_path_mp3 = "tmp/" + identif + ".mp3"
        duration = aitools.text_to_wav(file_path_wav, text)
        #subprocess.run(["ffmpeg", "-i", file_path_mp3, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        

        #os.remove(file_path_wav)
        dbutils.update_seconds(session["google_token"]["userinfo"]["email"], duration)

        response = Response(generate(file_path_wav), mimetype="audio/x-wav")
        
        return response


@app.route('/profile',methods = ['GET'])
@login_required
def profile():
    if request.method == 'GET':
        current_sec = dbutils.get_seconds(session["google_token"]["userinfo"]["email"])
        purchased_sec = dbutils.get_purchased_seconds(session["google_token"]["userinfo"]["email"])
        seconds_left = purchased_sec - current_sec
        hours, minutes, seconds = utils.get_time(current_sec)
        hours_l, minutes_l, seconds_l = utils.get_time(seconds_left)
        return render_template('profile.html', title='Welcome',  seconds=seconds, minutes=minutes, hours=hours, seconds_l=seconds_l, minutes_l=minutes_l, hours_l=hours_l, username=session["google_token"]["userinfo"]["given_name"])  

@app.route('/purchase',methods = ['POST'])
@login_required
def purchase():
    if request.method == 'POST':
        dbutils.new_payment(session["google_token"]["userinfo"]["email"],str(uuid.uuid4()), 5.0, 3600)
        return redirect(url_for("profile"))

"""
@app.route('/tokens_consumed',methods = ['GET'])
@login_required
def n_tokens():
    if request.method == 'GET':
        current_tokens = dbutils.get_tokens(session["google_token"]["userinfo"]["email"])

        return {"tokens": current_tokens}

@app.route('/time_consumed',methods = ['GET'])
@login_required
def n_seconds():
    if request.method == 'GET':
        current_sec = dbutils.get_seconds(session["google_token"]["userinfo"]["email"])

        return {"tokens": current_sec}
"""

@app.route('/login/')
def google():

    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)

    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/logout/')
def logout():

    session.pop("google_token", None)
    return redirect(url_for("home"))

@app.route('/login/callback')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = token["userinfo"]
    #print(" Google User ", user)
    #print(oauth.google.get(token))
    session['google_token'] = token

    
    dbutils.login_user(token["userinfo"]["email"])

    return redirect('/free')

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
