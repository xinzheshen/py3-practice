#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import traceback
import shutil


def delete_file(file_path):
    if os.path.exists(file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            shutil.rmtree(file_path)
        print('Successfully delete ' + file_path)
    else:
        print('The file does not exist.')


def process_argv():
    parser = argparse.ArgumentParser(prog='xls2xml')
    parser.add_argument('--file', '-f',
                        help='The file or folder to delete.',
                        required=True)
    return parser.parse_args()


if __name__ == '__main__':
    try:
        arg = process_argv()
        file_path = arg.file
        delete_file(file_path)
    except Exception as e:
        print(e)
        traceback.print_exc()
