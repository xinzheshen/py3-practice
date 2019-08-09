import scipy
import librosa
import numpy as np

sample_rate_bench, signal_bench = scipy.io.wavfile.read(r"D:\cats\audios\chimes\615_715\615.wav")
sample_rate_src, signal_src = scipy.io.wavfile.read(r"D:\cats\audios\chimes\615_715\stop_sleep5000ms.wav")


frame_length = signal_bench.shape[0]

frames_bench = librosa.util.frame(signal_bench, frame_length=frame_length)
frames_src = librosa.util.frame(signal_src, frame_length=frame_length)


res = np.correlate(signal_src, signal_bench, mode='valid')

max_value_index = np.argmax(res)

print(max_value_index)

max_value_time = max_value_index / sample_rate_src
print(str(max_value_time))


