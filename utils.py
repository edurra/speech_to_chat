import wave
import contextlib
import math

def get_wav_duration(path):
	with contextlib.closing(wave.open(path,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	return duration

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