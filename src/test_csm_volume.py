import argparse
import sys
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

SCREEN_SIZE = 10

SCREEN_SIZE_8_INCH = "1280x768"
# Volume process bar coordinate
START_X_8_INCH = 137
END_X_8_INCH = 1143
Y_8_INCH = 690

SCREEN_SIZE_10_INCH = "1920x1080"
START_X_10_INCH = 197
END_X_10_INCH = 1725
Y_10_INCH = 945

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


def tune_csm_volume(volume, device=None, first=False):
    global SCREEN_SIZE
    print("Tuning the csm volume....")
    logging.info("tuning the csm volume....")

    if SCREEN_SIZE == 8:
        x = int(volume / 100 * (END_X_8_INCH - START_X_8_INCH) + START_X_8_INCH)
        y = Y_8_INCH
    else:
        x = int(volume / 100 * (END_X_10_INCH - START_X_10_INCH) + START_X_10_INCH)
        y = Y_10_INCH

    if device:
        volume_up_cmd = "adb -s %s shell input keyevent 24" % device
        volume_down_cmd = "adb -s %s shell input keyevent 25" % device
    else:
        volume_up_cmd = "adb shell input keyevent 24"
        volume_down_cmd = "adb shell input keyevent 25"

    execute_cmd(volume_up_cmd)
    click_screen(x, y, device=device)

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
    execute_cmd(click_cmd)


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
    # if device:
    #     stop_cmd = "adb -s %s shell pm clear com.gm.vr" % device
    # else:
    #     stop_cmd = "adb shell pm clear com.gm.vr"
    if SCREEN_SIZE == 8:
        size = SCREEN_SIZE_8_INCH
    else:
        size = SCREEN_SIZE_10_INCH
    # click the x button
    x = int(int(size.split("x")[0]) - 3)
    y = 3

    click_screen(x, y, device=device)


def execute_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    exit_code = process.poll()
    if exit_code != 0:
        print("Fail to execute cmd: " + cmd + ", " + str(stderr, encoding='utf-8'))
        logging.error("Fail to execute cmd: " + cmd + ", " + str(stderr, encoding='utf-8'))
        sys.exit(1)
    return stdout, stderr, exit_code


def tap_coord_by_name_id(attrib_name, text_name):

    source = et.parse("./uidump.xml")
    root = source.getroot()

    for node in root.iter("node"):
        if node.attrib[attrib_name] == text_name:
            bounds = node.attrib["bounds"]
            pattern = re.compile(r"\d+")
            coord = pattern.findall(bounds)
            Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
            Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
            os.popen('adb shell input tap %s %s' % (str(Xpoint), str(Ypoint)))


if __name__ == '__main__':
    launch_VR()
    # time.sleep(1)
    # tune_csm_volume(50)
    # stop_VR()
    # time.sleep(0.5)

    os.popen(r'adb shell uiautomator dump --compressed /data/local/tmp/uidump.xml')
    os.popen(r'adb pull data/local/tmp/uidump.xml ')

    tap_coord_by_name_id("resource-id", "com.gm.vr:id/feedback_rings_small")
    time.sleep(2)

    tap_coord_by_name_id("resource-id", "com.gm.vr:id/exit")

