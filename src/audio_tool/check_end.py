
import argparse
import subprocess
import time


def judge_silence_detect_realtime_running():
    cmd = "wmic process where \"name like '%python%'\" get CommandLine | findstr realtimeDetectSilence.py"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in process.stdout.readlines():
        if "findstr" not in str(line, encoding='utf-8') and "realtimeDetectSilence.py" in str(line, encoding='utf-8') and "python" in str(line, encoding='utf-8'):
            return True
    return False


def process_argv():
    parser = argparse.ArgumentParser(prog='check_end')
    parser.add_argument('--synchronization', '-s', help='Synchronous execution or not, default is False.',
                        type=str2bool, nargs='?', const=False)
    return parser.parse_args()


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Unsupported value encountered.')


if __name__ == '__main__':
    arg = process_argv()
    if arg.synchronization:
        while True:
            if not judge_silence_detect_realtime_running():
                break
            else:
                time.sleep(2)
        print("realtimeDetectSilence.py stopped.")
    else:
        time.sleep(1)
        if judge_silence_detect_realtime_running():
            print("realtimeDetectSilence.py is running.")
        else:
            print("realtimeDetectSilence.py stopped.")
            exit(1)

