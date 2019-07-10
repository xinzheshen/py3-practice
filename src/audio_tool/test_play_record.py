import sounddevice as sd
from scipy.io import wavfile

SAMPLE_RATE = 44100
RECORD_OUTPUT_FILENAME = "sample_audio.wav"


def record(duration):
    recording = sd.rec(int(duration * SAMPLE_RATE), channels=1)
    sd.wait()
    wavfile.write(RECORD_OUTPUT_FILENAME, SAMPLE_RATE, recording)


def play():
    audio_file = r'D:\cats\bugs\setup\sample_audio.wav'
    sample_rate, signal = wavfile.read(audio_file)
    sd.play(signal, sample_rate, blocking=True)
