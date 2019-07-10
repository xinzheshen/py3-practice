# -*- coding: utf-8 -*-

import argparse
import re
import signal
import subprocess
import sys
import logging
import os
import time
from threading import Thread, Condition

from datetime import datetime
try:
    from pytz import timezone
    import soundcard as sc
except ImportError:
    import pkgs
    from pytz import timezone
    import soundcard as sc


VERSION = "1.0.0"

PC_TIMESTAMP = None
ADB_TIMESTAMP = None
ADB_TIMEZONE = None
START_TIME_STRING = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
AUDIO_FILE_NAME = "record_%s.wav" % START_TIME_STRING
OUTPUT_LOG = "silence_detect_realtime_%s.log" % START_TIME_STRING
END_TAG_FILE = "end.tag"
DEFAULT_OUTPUT_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), "output")
if not os.path.exists(DEFAULT_OUTPUT_PATH):
    os.mkdir(DEFAULT_OUTPUT_PATH)
TIMESTAMP_FILE_POSTFIX = ".ts"
FFMPEG_CMD = """ffmpeg -f dshow -i audio="%s" -ar 16000.0 -ac 1 -af silencedetect=noise=%fdB:d=%f %s"""

ADB_DEVICE_ID = 'xxxxxxxxxxxxxxxxxxx'
ADB_CMD_TIME = 'adb -s %s shell echo $EPOCHREALTIME' % ADB_DEVICE_ID
ADB_CMD_TIMEZONE = 'adb -s %s shell getprop persist.sys.timezone' % ADB_DEVICE_ID


class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        logging_config(os.path.join(DEFAULT_OUTPUT_PATH, OUTPUT_LOG))
        printError(message)
        exit(2)


def logging_config(file_name):
    logging.basicConfig(level=logging.DEBUG,
                        filename=file_name,
                        filemode='a',
                        format='%(levelname)s: %(message)s'
                        )


def printInfo(msg):
    print(msg)
    logging.info(msg)


def printDebug(msg):
    print(msg)
    logging.debug(msg)


def printWarning(msg):
    print(msg)
    logging.warning(msg)


def printError(msg):
    print(msg)
    logging.error(msg)


class RecordAndDetectSilence(object):
    def __init__(self, cmd):
        self.exitcode = 0
        self.has_silence = False
        self.recorder_th = None
        self.catch_log_th = None
        self.check_end_tag_th = None
        self.kill_ffmpeg_th = None
        self.ffmpeg_process = None
        self._cmd = cmd
        self.con = Condition()
        self.end_tag = False
        self.finish = False

    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.recorder_th = Thread(target=self._record_and_detect_silence, daemon=True)
        self.recorder_th.start()

        self.catch_log_th = Thread(target=self._catch_log)
        self.catch_log_th.start()

        self.check_end_tag_th = Thread(target=self._check_end_tag, daemon=True)
        self.check_end_tag_th.start()

        self.kill_ffmpeg_th = Thread(target=self._kill_ffmpeg_process, daemon=True)
        self.kill_ffmpeg_th.start()

    def signal_handler(self, signal, frame):
        printDebug('enter _signal_handler')
        self.end_tag = True
        # time.sleep(1)
        with self.con:
            self.con.notify_all()
        while not recorder.finish:
            pass
        if self.has_silence:
            exit(100)
        else:
            exit(self.exitcode)

    def _record_and_detect_silence(self):
        self.ffmpeg_process = subprocess.Popen(self._cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # while self.ffmpeg_process.poll() is None:
        line = self.ffmpeg_process.stderr.readline().strip()
        while line:
            res_silence = re.match(r'^\[silencedetect.+\] (.*)', line)
            if res_silence:
                text = res_silence.group(1)
                self.has_silence = True
                if "start" in text:
                    with self.con:
                        self.con.notify_all()
                        printInfo("="*40 + "audio drop start" + "="*40)
                        if "-" in text:
                            text = text[:text.index("-")] + "0"
                else:
                    printInfo("="*40 + "audio drop end" + "="*40)
                # printInfo(text)
                self._format_output(text)
            elif self._ignore_output(line):
                pass
            else:
                printInfo(line)
            line = self.ffmpeg_process.stderr.readline().strip()

        self.exitcode = self.ffmpeg_process.poll()
        printDebug("ffmpeg exitcode:" + str(self.exitcode))
        self.finish = True

    def _catch_log(self):
        while self.recorder_th is not None and self.recorder_th.isAlive() and not self.end_tag:
            with self.con:
                self.con.wait()
            if not self.end_tag:
                self._download_log()
        printDebug("Finish _catch_log")

    def _download_log(self):
        # simulate downloading log when audio drop
        printInfo("Downloading log...")
        time.sleep(5)
        printInfo("Finish download log...")

    def _ignore_output(self, line):
        if line == "" or line.startswith("size=") or line.startswith("configuration") \
                or line.startswith("libavutil") or line.startswith("libavcodec") \
                or line.startswith("libavformat") or line.startswith("libavdevice") \
                or line.startswith("libavfilter") or line.startswith("libavresample") \
                or line.startswith("libswscale") or line.startswith("libswresample"):
            return True
        return False

    def _format_output(self, text):
        out = text.replace("silence", "audio_drop").split("|")
        second = int(float(out[0].split(":")[1].strip()))
        result = []
        result.append(out[0].strip() + "s")
        try:
            if PC_TIMESTAMP:
                result.append("  pc_time:")
                result.append(self._process_time(PC_TIMESTAMP, second))
        except:
            result.remove("  pc_time:")

        try:
            if ADB_TIMESTAMP and ADB_TIMEZONE:
                result.append("  adb_time:")
                result.append(self._process_time(ADB_TIMESTAMP, second, time_zone=ADB_TIMEZONE))
        except:
            result.remove("  adb_time:")

        printInfo(" ".join(result))
        if len(out) > 1:
            printInfo(out[1].strip() + "s")

    def _process_time(self, timestamp, second, time_zone=None):
        result_time = ""
        timestamp = timestamp + second
        if time_zone:
            # result_time = str(datetime.utcfromtimestamp(timestamp))
            result_time = str(timezone('Atlantic/Azores').localize(datetime.utcfromtimestamp(timestamp)).astimezone(timezone(time_zone)))[:-6]
        else:
            time_list = time.localtime(timestamp)
            result_time = time.strftime("%Y-%m-%d %H:%M:%S", time_list)
        return result_time

    def _kill_ffmpeg_process(self):
        while True:
            if self.end_tag and self.ffmpeg_process and self.recorder_th.isAlive():
                printDebug("To kill ffmpeg process...")
                self.ffmpeg_process.stdin.write("q\n")
                self.ffmpeg_process.stdin.close()
                break

    def _check_end_tag(self):
        while True:
            if os.path.exists(os.path.join(DEFAULT_OUTPUT_PATH, END_TAG_FILE)):
                printDebug("end.tag exits.")
                self.end_tag = True
                break
        printDebug("Finish _check_end_tag")


def get_csm_timestamp():
    global ADB_TIMESTAMP, ADB_TIMEZONE
    try:
        timestamp = exec_command(ADB_CMD_TIME)
        if timestamp and timestamp[0].isdigit() and "." in timestamp:
            ADB_TIMESTAMP = int(float(timestamp))

        timezone = exec_command(ADB_CMD_TIMEZONE)
        if timezone and timezone[0].isupper() and "/" in timezone:
            ADB_TIMEZONE = timezone
    except Exception:
        pass
    if not ADB_TIMESTAMP:
        printWarning("Can't get the adb timestamp.")
    if not ADB_TIMEZONE:
        printWarning("Can't get the adb timezone.")


def exec_command(command):
    result = ""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = process.stdout.readlines()
    stderr = process.stderr.readlines()
    if stderr:
        printWarning(stderr)
    elif stdout:
        result = stdout[0].decode().strip()
    else:
        pass
    return result


def get_default_mic_device():
    default_mic_name = ""
    try:
        default_mic_name = sc.default_microphone().name
    except:
        pass
    return default_mic_name


def process_argv():
    parser = MyArgumentParser(prog='realtimeDetectSilence')
    parser.add_argument('--volume', '-v', help='The threshold of volume(dB)., between -60 and 0, default is -45.', type=float, default=-45, required=False)
    parser.add_argument('--duration', '-d', help='Set silence duration until notification.', type=float, default=2, required=False)
    return parser.parse_args()


if __name__ == '__main__':
    arg = process_argv()
    mic_device = get_default_mic_device()
    if mic_device:
        printWarning("Use the default microphone device to record: " + mic_device)
    else:
        printWarning("There is not default microphone device to record.")
        exit(3)

    if -60 <= arg.volume <= 0:
        get_csm_timestamp()
        PC_TIMESTAMP = int(time.time())
        printInfo("="*10 + "Start detect audio drop of file: " + AUDIO_FILE_NAME + "="*10)
        cmd = FFMPEG_CMD % (mic_device, arg.volume, arg.duration, os.path.join(DEFAULT_OUTPUT_PATH, AUDIO_FILE_NAME))
        printInfo(cmd)
        recorder = RecordAndDetectSilence(cmd)
        recorder.run()
        # recorder.recorder_th.join()
        while not recorder.finish:
            pass
        recorder.signal_handler(None, None)
    else:
        printError("The param volume(v) should be between -60 and 0.")
        exit(1)

