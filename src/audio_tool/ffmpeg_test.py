import re
import subprocess
import sys
from ffmpy import FFmpeg
from threading import Thread
from queue import Queue, Empty

class NonBlockingStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    raise UnexpectedEndOfStream

        self._t = Thread(target = _populateQueue,
                         args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None, timeout = timeout)
        except Empty:
            return None

class UnexpectedEndOfStream(Exception):
    pass


def execute_cmd(cmd, get_max_volume=False):
    from subprocess import Popen, PIPE
    from time import sleep


    # run the shell as a subprocess:
    p = Popen(cmd, stdout = PIPE, stderr = PIPE, shell = False)
    # wrap p.stdout with a NonBlockingStreamReader object:
    nbsr = NonBlockingStreamReader(p.stderr)
    # issue command:
    # p.stdin.write('command\n')
    # get the output
    while True:
        output = nbsr.readline(1) # 0.1 secs to let the shell output the result
        # if not output:
        #     print('[No more data]')
        #     break
        print(output)


def execute_cmd1(cmd):
    procExe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    while procExe.poll() is None:
        line = procExe.stderr.readline()
        print(line)
    print("exitcode", procExe.poll())



if __name__ == '__main__':

    cmd = """ffmpeg -f dshow -i audio="Microphone (3- CE-LINK)" -ar 16000.0 -ac 1 -af silencedetect=noise=0.01:d=1 out2.wav"""
    # execute_cmd(cmd)
    # ff = FFmpeg(inputs={'audio="Microphone (3- CE-LINK)"': "-f dshow"}, outputs={'out.wav': "-ar 16000.0 -ac 1 -af silencedetect=noise=-50dB:d=1"})
    # print(ff.cmd)
    # ff.run()

    execute_cmd1(cmd)