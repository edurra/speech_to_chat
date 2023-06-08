import wave
import contextlib

def get_wav_duration(path):
	with contextlib.closing(wave.open(path,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	return duration