from flask import render_template, request, redirect
from flask import Flask, session, Response, url_for
import json
import os
import uuid
import requests
import subprocess
import aitools

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
def index():
    if request.method == 'GET':
        session["messages"] = []
        session["count"] = 0
        return render_template('index.html', title='Welcome', mode="Free Chat Mode", username=session["google_token"]["userinfo"]["given_name"])

@app.route('/chat', methods = ['POST', 'GET'])
@login_required
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
        text = aitools.speech_recognize_once_from_file(file_path_wav)
        os.remove(file_path)
        os.remove(file_path_wav)
        session["messages"].append({"role": "user", "content": text})
        assistant_response = aitools.free_talk(session["messages"])
        session["messages"].append({"role": "assistant", "content": assistant_response})

        if len(session["messages"]) > max_messages:
            session["messages"] =  session["messages"][len(session["messages"]) - max_messages + 1:len(session["messages"])]
        
        return json.dumps(session["messages"][len(session["messages"])-2:len(session["messages"])])
        
        #return json.dumps([{"a": "b"}])

@app.route('/random', methods = ['POST', 'GET'])
@login_required
def random():
    if request.method == 'POST':
        
        session["count"] += 1

        assistant_message = aitools.random_topic()
        session["messages"].append({"role": "assistant", "content": assistant_message})

        
        return json.dumps(session["messages"])
        
        #return [{"a":"b"}]
    if request.method == 'GET':
        
        session["messages"] = []
        session["count"] = 0
        return render_template('random.html', title='Welcome', mode="Random Topic Mode", username=session["google_token"]["userinfo"]["given_name"])

@app.route('/job_interview', methods = ['POST', 'GET'])
@app.route('/job_interview_init', methods = ['POST', 'GET'])
@login_required
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

            interviewer_message = aitools.job_interview(job_position, session["messages"])
            session["messages"].append({"role": "assistant", "content": interviewer_message})
            return json.dumps(session["messages"])
        
        if request.path == "/job_interview":
            session["count"] += 1
            print("post received")
            print(request)
            
            audio_file = request.files['audio_file']
            identif = str(uuid.uuid4())
            file_path = "tmp/" + identif + ".mp3"
            audio_file.save(file_path)
            file_path_wav = "tmp/" + identif + ".wav"
            subprocess.run(["ffmpeg", "-i", file_path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            text = aitools.speech_recognize_once_from_file(file_path_wav)
            os.remove(file_path)
            os.remove(file_path_wav)
            session["messages"].append({"role": "user", "content": text})
            assistant_response = aitools.job_interview(session["job_position"], session["messages"])
            session["messages"].append({"role": "assistant", "content": assistant_response})

            if len(session["messages"]) > max_messages:
                session["messages"] =  session["messages"][len(session["messages"]) - max_messages + 1:len(session["messages"])]
        
        return json.dumps(session["messages"][len(session["messages"])-2:len(session["messages"])])

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
@login_required
def audio():
    if request.method == 'GET':
        print("get received")
        print(request)
        #print(session["messages"])
        text = session["messages"][len(session["messages"])-1]["content"]
        identif = str(uuid.uuid4())
        file_path = "tmp/" + identif + ".wav"
        #file_path = "tmp/test2.wav"
        aitools.text_to_audio(file_path, text)

        response = Response(generate(file_path), mimetype="audio/x-wav")
        
        return response



@app.route('/login/')
def google():

    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    print(redirect_uri)
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
    return redirect('/free')

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
