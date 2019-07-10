import argparse
import sys
import clr
import pyaudio
import wave
import subprocess
import os
import logging
import time
# import sounddevice as sd
# from scipy.io import wavfile
import configparser
import traceback
import xml.etree.cElementTree as et
import re

AUDIO_CTRL_OBJ = None

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
RECORD_OUTPUT_FILENAME = "recorded_audio.wav"
SPEECH_RECOGNIZE_EXE = "speech-recognize/SpeechRecognizeBin.exe"

SCREEN_SIZE = 8

SCREEN_SIZE_8_INCH = "1280x768"
# Volume process bar coordinate
START_X_8_INCH = 137
END_X_8_INCH = 1143
Y_8_INCH = 690

SCREEN_SIZE_10_INCH = "1920x1080"
START_X_10_INCH = 197
END_X_10_INCH = 1725
Y_10_INCH = 945

LISTENER_RESOURCE_ID = "com.gm.vr:id/sr_icon"
EXIT_VR_RESOURCE_ID = "com.gm.vr:id/exit"

CURRENT_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_LOG = "SetupVREnv.log"
DEFAULT_OUTPUT_PATH = os.path.join(CURRENT_PATH, OUTPUT_LOG)
logging.basicConfig(level=logging.INFO,
                    filename=DEFAULT_OUTPUT_PATH,
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )


class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        logging.error(message)
        sys.exit(2)


def load_dll():
    print("Loading dll...")
    logging.info("Loading dll...")
    global AUDIO_CTRL_OBJ
    sys.path.append("./dlls")
    clr.FindAssembly("AudioSwitcher.AudioApi.CoreAudio.dll")
    from AudioSwitcher.AudioApi.CoreAudio import CoreAudioController
    AUDIO_CTRL_OBJ = CoreAudioController()


def tune_mic_volume(volume):
    global AUDIO_CTRL_OBJ
    mic_device = AUDIO_CTRL_OBJ.DefaultCaptureDevice
    if mic_device:
        mic_device.Volume = volume
        print('The default microphone volume is set to ' + str(volume))
        logging.info('The default microphone volume is set to ' + str(volume))
    else:
        print('There is not microphone device.')
        logging.error('There is not microphone device.')
        sys.exit(1)


def tune_speaker_volume(volume):
    global AUDIO_CTRL_OBJ
    speaker_device = AUDIO_CTRL_OBJ.DefaultPlaybackDevice
    if speaker_device:
        speaker_device.Volume = volume
        print('The default speaker volume is set to ' + str(volume))
        logging.info('The default speaker volume is set to ' + str(volume))
    else:
        print('There is not speaker device.')
        logging.error('There is not speaker device.')
        sys.exit(1)


def tune_csm_volume(volume, device=None):
    global SCREEN_SIZE

    if SCREEN_SIZE == 8:
        x = int(volume / 100 * (END_X_8_INCH - START_X_8_INCH) + START_X_8_INCH)
        y = Y_8_INCH
    else:
        x = int(volume / 100 * (END_X_10_INCH - START_X_10_INCH) + START_X_10_INCH)
        y = Y_10_INCH

    if device:
        volume_up_cmd = "adb -s %s shell input keyevent 24" % device
    else:
        volume_up_cmd = "adb shell input keyevent 24"

    execute_cmd(volume_up_cmd)
    click_screen(x, y, device=device)
    print('The CSM volume is set to ' + str(volume))
    logging.info('The CSM volume is set to ' + str(volume))
    # # csm need tune 63 times from volume max to mute
    # total_times = 63
    #
    # # first tune to mute
    # count = 0
    # while count < total_times:
    #     execute_cmd(volume_down_cmd)
    #     count += 1
    # print("Turn down the volume times: " + str(count))
    # logging.info("Turn down the volume times: " + str(count))
    # # then tune to specified volume
    # tune_times = int(int(volume) * total_times / 100)
    # print("Set CSM volume to " + str(volume) + ", need turn-up times:" + str(tune_times))
    # count = 0
    # while count < tune_times:
    #     execute_cmd(volume_up_cmd)
    #     count += 1
    # print("Turn up the volume times: " + str(count))
    # logging.info("Turn up the volume times: " + str(count))


def play_and_record(cfg):
    # To ensure the VR is in listening mode, need to run two times to click
    count = 0
    while count < 2:
        count += 1
        get_ui_dump(device=cfg["DEVICE"])
        get_result, x, y = get_coord_by_resource_id(LISTENER_RESOURCE_ID)
        if get_result:
            click_screen(x, y, device=cfg["DEVICE"])
            break

    play(cfg["PLAY_AUDIO"])
    record(int(cfg["RECORD_DURATION"]))


def record(duration):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")
    logging.debug("Recording...")

    frames = []

    for i in range(0, int(SAMPLE_RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(RECORD_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Done recording: " + RECORD_OUTPUT_FILENAME)
    logging.info("Done recording: " + RECORD_OUTPUT_FILENAME)


def play(audio_file):
    wf = wave.open(audio_file, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    print("Playing the audio: " + audio_file)
    logging.info("Playing the audio: " + audio_file)

    data = wf.readframes(CHUNK)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Done playing")
    logging.info("Done playing")


def get_screen_size(device=None):
    global SCREEN_SIZE
    if device:
        get_screen_size_cmd = "adb -s %s shell wm size" % device
    else:
        get_screen_size_cmd = "adb shell wm size"

    stdout, stderr, _ = execute_cmd(get_screen_size_cmd)

    size = str(stdout, encoding='utf8').split(" ")[2].replace("\r", "").replace("\n", "")
    print("The screen size: " + size)
    logging.info("The screen size: " + size)
    if size == SCREEN_SIZE_8_INCH:
        SCREEN_SIZE = 8
    elif size == SCREEN_SIZE_10_INCH:
        SCREEN_SIZE = 10
    else:
        print("Do not support this screen size")
        logging.error("Do not support this screen size")
        sys.exit(1)


def click_screen(x, y, device=None):
    if device:
        click_cmd = "adb -s %s shell input tap %d %d" % (device, x, y)
    else:
        click_cmd = "adb shell input tap %d %d" % (x, y)
    print("To click the screen: %d %d" % (x, y))
    logging.info("To click the screen: %d %d" % (x, y))
    execute_cmd(click_cmd)


def get_ui_dump(device=None):
    if device:
        dump_cmd = r"adb -s %s shell uiautomator dump --compressed /data/local/tmp/uidump.xml" % device
        pull_cmd = r"adb -s %s pull data/local/tmp/uidump.xml" % device
    else:
        dump_cmd = r"adb shell uiautomator dump --compressed /data/local/tmp/uidump.xml"
        pull_cmd = r"adb pull data/local/tmp/uidump.xml"

    execute_cmd(dump_cmd)
    execute_cmd(pull_cmd)


def get_coord_by_resource_id(text_name):
    source = et.parse("./uidump.xml")
    root = source.getroot()
    Xpoint = 0
    Ypoint = 0
    get_result = False
    for node in root.iter("node"):
        if node.attrib["resource-id"] == text_name:
            bounds = node.attrib["bounds"]
            pattern = re.compile(r"\d+")
            coord = pattern.findall(bounds)
            Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
            Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
            get_result = True
            break
    if not get_result:
        print("Can not get the resource-id: " + text_name)
        logging.error("Can not get the resource-id: " + text_name)
    return get_result, Xpoint, Ypoint


def launch_VR(device=None):
    global SCREEN_SIZE
    get_screen_size(device=device)
    if SCREEN_SIZE == 8:
        size = SCREEN_SIZE_8_INCH
    else:
        size = SCREEN_SIZE_10_INCH
    # cal the center coordinate of the screen
    x = int(int(size.split("x")[0])/2)
    y = int(int(size.split("x")[1])/2)
    if device:
        start_cmd = "adb -s %s shell am start -n com.gm.vr/.PTTActivity" % device
    else:
        start_cmd = "adb shell am start -n com.gm.vr/.PTTActivity"

    stdout, stderr, _ = execute_cmd(start_cmd)
    # even though the exit_code is 0, there may be error.
    tmp = str(stderr, encoding='utf-8').split("\r\n")
    if len(tmp) > 1 and "Error" in tmp[0]:
        print("Launch the VR failed, " + tmp[1])
        logging.error("Launch the VR failed, " + tmp[1])
        sys.exit(1)

    time.sleep(0.5)
    click_screen(x, y, device=device)


def stop_VR(device=None):
    _, x, y = get_coord_by_resource_id(EXIT_VR_RESOURCE_ID)
    click_screen(x, y, device=device)
    # if device:
    #     stop_cmd = "adb -s %s shell pm clear com.gm.vr" % device
    # else:
    #     stop_cmd = "adb shell pm clear com.gm.vr"
    # execute_cmd(stop_cmd)


def execute_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    exit_code = process.poll()
    if exit_code != 0:
        print("Fail to execute cmd: " + cmd + ",\n " + str(stderr, encoding='utf-8'))
        logging.error("Fail to execute cmd: " + cmd + ",\n " + str(stderr, encoding='utf-8'))
        sys.exit(1)
    return stdout, stderr, exit_code


def speech_recognize(audio_file, grammar, expect_result):
    # audio_file = r"D:\cats\bugs\setup\SetupVREnv\sample_audio.wav"
    cmd = "%s -d -i %s -g %s" % (SPEECH_RECOGNIZE_EXE, audio_file, grammar)
    print("To execute cmd: " + cmd)
    logging.info("To execute cmd: " + cmd)
    stdout, stderr, _ = execute_cmd(cmd)
    recognized = False
    confidence = 0
    for line in str(stdout, encoding='utf-8').split("\r\n"):
        if "I guess you said" in line:
            print(line)
            logging.info(line)
            if line.split(":")[1] == expect_result:
                recognized = True
                break
        if "Recognize Rejected:" in line:
            confidence = line.split(",")[1].split(":")[1].strip()
            print(line)
            logging.info(line)
            break
    return recognized, int(confidence)


def show_window(msg):
    import tkinter
    win = tkinter.Tk()
    win.title('Setup VR Env')
    win.geometry('300x50+600+350')
    win.resizable(width=False, height=False)
    # add label
    msg_label = tkinter.Label(win, text=msg, font=("黑体", 16))
    msg_label.pack()

    win.mainloop()


def loop(mic_volume, speaker_volume, csm_volume, cfg):
    tune_mic_volume(mic_volume)
    tune_speaker_volume(speaker_volume)
    launch_VR(device=cfg["DEVICE"])
    time.sleep(0.5)
    tune_csm_volume(csm_volume, device=cfg["DEVICE"])
    play_and_record(cfg)
    stop_VR(device=cfg["DEVICE"])
    return speech_recognize(RECORD_OUTPUT_FILENAME, cfg["GRAMMAR_FILE"], cfg["EXPECT_RESULT"])


def main():
    cfg = get_configuration()

    volume_min = 0
    volume_max = 100

    mic_volume = int(cfg["MICROPHONE"])
    speaker_volume = int(cfg["SPEAKER"])
    csm_volume = int(cfg["CSM"])
    if mic_volume < volume_min or mic_volume > volume_max \
            or speaker_volume < volume_min or speaker_volume > volume_max \
            or csm_volume < volume_min or csm_volume > volume_max:
        print("Volume value should be between 0 and 100.")
        logging.error("Volume value should be between 0 and 100.")
        sys.exit(1)

    load_dll()
    recognize_result = False
    recognize_result, confidence = loop(mic_volume, speaker_volume, csm_volume, cfg)

    if recognize_result:
        print("The VR env can work.")
        logging.info("*" * 30)
        logging.info("The VR env can work.")
        logging.info("*" * 30)
        show_window("The VR env can work!")
    else:
        print("The VR env can not work.")
        logging.info("*" * 30)
        logging.info("The VR env can not work.")
        logging.info("*" * 30)
        show_window("The VR env can not work!")


def get_configuration():
    vr_config = {}
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(CURRENT_PATH, "SetupVREnv.cfg"))

        vr_config["MICROPHONE"] = config.get("VOLUME", "MICROPHONE", fallback=60)
        vr_config["SPEAKER"] = config.get("VOLUME", "SPEAKER", fallback=70)
        vr_config["CSM"] = config.get("VOLUME", "CSM", fallback=70)
        vr_config["DEVICE"] = config.get("OTHERS", "DEVICE", fallback=None)
        vr_config["PLAY_AUDIO"] = config.get("OTHERS", "PLAY_AUDIO", fallback=None)
        vr_config["RECORD_DURATION"] = config.get("OTHERS", "RECORD_DURATION", fallback=10)
        vr_config["GRAMMAR_FILE"] = config.get("OTHERS", "GRAMMAR_FILE", fallback=None)
        vr_config["EXPECT_RESULT"] = config.get("OTHERS", "EXPECT_RESULT", fallback=None)
    except Exception as e:
        print("Configuration Error: %s" %e)
        logging.error("Configuration Error: %s" %e)
        print("Stack Trace: %s" % traceback.format_exc())
        logging.debug("Stack Trace: %s" % traceback.format_exc())
        sys.exit(1)

    return vr_config


if __name__ == '__main__':
    try:
        if "NODE_PROD" in os.environ:
            SPEECH_RECOGNIZE_EXE = os.path.join(os.environ["NODE_PROD"], SPEECH_RECOGNIZE_EXE)
        else:
            print("Can't find the SpeechRecognizeBin.exe")
            logging.error("Can't find the SpeechRecognizeBin.exe")
            sys.exit(1)

        main()
    except Exception as e:
        print("SetupVRENV Error: %s" %e)
        logging.error("SetupVRENV Error: %s" %e)
        print("Stack Trace: %s" % traceback.format_exc())
        logging.error("Stack Trace: %s" % traceback.format_exc())
        sys.exit(1)
