import argparse


def process_argv():
    parser = argparse.ArgumentParser(prog='vr_env_tuner')
    parser.add_argument('--device', '-d', help='The adb device of CSM', required=True)
    return parser.parse_args()


if __name__ == '__main__':
    arg = process_argv()
    print(arg.device)
