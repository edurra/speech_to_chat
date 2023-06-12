import wave
from mutagen.mp3 import MP3
import contextlib
import math
import subprocess

def get_wav_duration(path):
	with contextlib.closing(wave.open(path,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	return duration

"""
def get_mp3_duration(path):
	name = path.split(".")[0]
	file_path_wav = name + ".wav"
	subprocess.run(["ffmpeg", "-i", path, file_path_wav], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
	duration = get_wav_duration(file_path_wav)
	os.remove(file_path_wav)
	return duration
"""

def get_time(seconds):
	hours = 0
	minutes = 0
	if seconds > 3600:
		hours = math.floor(seconds/3600)
		seconds = seconds - hours*3600
	if seconds > 60:
		minutes = math.floor(seconds/60)
		seconds = seconds - minutes * 60
	return hours, minutes, seconds