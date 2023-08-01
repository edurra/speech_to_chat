# speech_to_chat

## Introduction
This application provides an interface to speak with ChatGPT. It has been conceived to provide users with a different way to study languages. The available modes are:
- Free talk: you start speaking about the topic you would like to discuss
- Random topic: the engine will suggest a random topic to talk about
- Job interview: you will input a job position and the application will simulate a job interview
- Vocabulary: the engine will propose you idioms and words so that you can explain their meaning
- Debate: the engine will suggest a controversial topic to debate about
The application will provide feedback about how well structured your sentences are and suggest improvements for them.

## Technologies
The application backend is written in Python (Flask) and uses basic JS, HTML and CSS (Bootstrap) for the frontend. In addition, data about users is stored in a MySQL server. The text-to-speech conversion is made via Google Cloud Services and the speech-to-text conversion leverages OpenAI's Whisper.

## How to run
### Prerequisites
There are several prerequisites to run the application. 
#### Database
You need to create a MySQL server and add its credentials as environment variables (MYSQL_USER, MYSQL_PASS and MYSQL_HOST). In addition, the following tables must be created:
- Table users -> create table users (email varchar 100, tokens_consumed integer, seconds_consumed integer);
- Table payments -> create table payments (id varchar(100) not null, email varchar(100), date datetime, amount double, primary key (id), foreign key(email) references users(email));
### Required software
- Python 3.X
- FFMPEG
### Dependencies
All dependencies must be installed via ´pip install -r requirements.txt´
### Environment variables
Apart form the database's environment variables, the following ones are needed.
#### OpenAI
It is necessary to create a OpenAI API Key for interaction with the ChatGPT engine. It must be set as the OPENAI_KEY environment variable.
### Google Cloud Platform
Google Cloud is used to provide:
- User authentication and authorization via OpenID Connect. For this, the API credentials must be stored at the environment variables GOOGLE_ID and GOOGLE_SECRET
- Text to speech conversion. For this, the GOOGLE_CREDENTIALS environment variable must contain the path to Google's in JSON format for the Text-to-speech API.
### Flask key
The FLASK_KEY environment variable must contain any randomly generated value. It is needed by Flask to run the application.


