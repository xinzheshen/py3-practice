import os
import subprocess
import numpy as np


def record():
    cmd = 'ffmpeg -f dshow -i audio="Microphone (2- CE-LINK)" -f s16le -ac 1 -ar 16000 -t 00:00:05 -'
    devnull = open(os.devnull)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=devnull)
    devnull.close()

    # scale = 1./float(1 << ((8 * 2) - 1))
    # y = scale * np.frombuffer(proc.stdout.read(), '<i2').astype(np.float32)
    y = np.frombuffer(proc.stdout.read(), '<i2')

    return y

result = record()
print("end")