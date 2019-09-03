#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import scipy.io.wavfile
from collections import OrderedDict
import sys
import time
import argparse

# whether the audio file has sound, yes(1), no(2)
exit_code_first = 2
# whether the sound changes to mute(1) , slowly_down(2), not_change(3)
exit_code_second = 0
# whether the sound recovers back after mute or slowly down, yes(1), no(2)
exit_code_third = 0

frame_size = 0.025
frame_stride = 0.01
n_fft = 1024


def calc_stft(signal, sample_rate=16000, winfunc=np.hamming):
    """
    在程序中, frame_size 为将信号分为较短的帧的大小, 在语音处理中, 通常帧大小在 20ms 到 40ms 之间. 这里设置为 25ms, 即 frame_size = 0.025;

　　frame_stride 为相邻帧的滑动尺寸或跳跃尺寸, 通常帧的滑动尺寸在 10ms 到 20ms 之间, 这里设置为 10ms, 即 frame_stride = 0.01. 此时, 相邻帧的交叠大小为 15ms;

　　窗函数采用汉明窗函数 (Hamming Function) ;

　　在每一帧, 进行 512 点快速傅里叶变换, 即 NFFT = 512
    :param signal:
    :param sample_rate:
    :param frame_size:
    :param frame_stride:
    :param winfunc:
    :param n_fft:
    :return:
    """
    # Calculate the number of frames from the signal
    frame_length = frame_size * sample_rate
    frame_step = frame_stride * sample_rate
    signal_length = len(signal)
    frame_length = int(round(frame_length))
    frame_step = int(round(frame_step))
    num_frames = 1 + int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))
    # zero padding
    pad_signal_length = num_frames * frame_step + frame_length
    z = np.zeros((pad_signal_length - signal_length))
    # Pad signal to make sure that all frames have equal number of samples
    # without truncating any samples from the original signal
    pad_signal = np.append(signal, z)

    # Slice the signal into frames from indices
    indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]
    # Get windowed frames
    frames *= winfunc(frame_length)
    # Compute the one-dimensional n-point discrete Fourier Transform(DFT) of
    # a real-valued array by means of an efficient algorithm called Fast Fourier Transform (FFT)
    tmp = np.fft.rfft(frames, n_fft)
    mag_frames = np.absolute(tmp)
    # Compute power spectrum
    pow_frames = (1.0 / n_fft) * ((mag_frames) ** 2)

    return pow_frames


def detect_mix_for_audio_only_with_single_freq(pow_spec):
    result = OrderedDict()

    start_time = 0
    last_valid_freq = 0
    last_valid_freq_power = 0
    number = 0
    first_time = True
    for index_time, powers in enumerate(pow_spec):
        index_time = index_time * frame_stride
        max_power_freq_index = np.argmax(powers)
        max_power = powers[max_power_freq_index]
        # Normally the power should be bigger than 5000 when there is voice
        if max_power > 5000:
            valid_frequencies = np.where(powers > max_power * 0.9)
            max_freq = max(valid_frequencies[0])
            min_freq = min(valid_frequencies[0])

            # The audio is single freq, but the got data may not be single.
            if abs(max_power_freq_index - last_valid_freq) < 2:
                duration = str(start_time) + '-' + str(index_time)
            else:
                start_time = index_time
                number += 1
                duration = str(start_time) + '-' + str(index_time)
                if first_time:
                    first_time = False
                elif powers[last_valid_freq] >= last_valid_freq_power:
                    sys.stderr.write('The time of mixing sound: ' + str(index_time))
                    exit(100)
            if number == 0:
                number += 1
            result[number] = duration
            last_valid_freq = max_power_freq_index
            last_valid_freq_power = max_power
    return result


def detect_mix_for_audio_with_single_and_multi_freq(pow_spec):
    global exit_code_first
    result = OrderedDict()
    start = 0
    number = 0
    flag = True
    new_section = True
    multi_freq_section = False
    max_valid_freq = 0
    current_section_is_single = True
    last_section_is_single = True

    # hard code
    base_power = 5000
    base_power_scale = 0.0001
    freq_scope = int(n_fft / 4)
    single_freq_threshold = 400

    for index, powers in enumerate(pow_spec):
        max_power_freq_index = np.argmax(powers)
        max_power = powers[max_power_freq_index]
        max_valid_freq = max_valid_freq if (max_valid_freq > max_power_freq_index) else max_power_freq_index
        # Normally the power should be bigger than base_power when there is voice
        if max_power > base_power:
            exit_code_first = 1
            valid_frequencies = np.where(powers > max_power * base_power_scale)
            max_freq = max(valid_frequencies[0])
            min_freq = min(valid_frequencies[0])

            if index == 143:
                print(max_freq, min_freq)

            # judge the valid freq scope, if true, it says it's the same audio
            if (max_freq - min_freq) < freq_scope:
                if flag:
                    flag = False
                    new_section = True

                # Judge if it's in multi_freq_section, and not mix
                elif max_power_freq_index < single_freq_threshold:
                    if not multi_freq_section:
                        multi_freq_section = True
                        new_section = True
            else:
                if not flag:
                    flag = True
                    new_section = True
                if multi_freq_section:
                    multi_freq_section = False
            if new_section:
                new_section = False
                if number == 0:
                    number += 1
                    start = index
                    if max_power_freq_index < single_freq_threshold:
                        current_section_is_single = False
                else:
                    last_result = result[number]
                    # Sometimes there is silence in chime, assume the silence is less than 10（0.1 second）
                    if last_result[1] - last_result[0] > 10:
                        number += 1
                        start = index
                        current_section_is_single = not last_result[2]

            result[number] = [start, index, current_section_is_single]
    return result, max_valid_freq


def analyze_every_section(pow_spec, result, max_freq, multi_freq_section=2):
    global exit_code_second, exit_code_third
    if len(result) == 3:
        first_duration = result[1]
        first_duration_mean_power_of_max_freq = np.mean(pow_spec[first_duration[0]: first_duration[1], max_freq])

        second_duration = result[2]
        second_duration_mean_power_of_max_freq = np.mean(pow_spec[second_duration[0]: second_duration[1], max_freq])

        third_duration = result[3]
        third_duration_mean_power_of_max_freq = np.mean(pow_spec[third_duration[0]: third_duration[1], max_freq])

        second_diff_ratio = abs(first_duration_mean_power_of_max_freq - second_duration_mean_power_of_max_freq) / first_duration_mean_power_of_max_freq
        if second_diff_ratio > 0.99:
            exit_code_second = 1
        elif second_diff_ratio > 0.1:
            exit_code_second = 2
        else:
            exit_code_second = 3
        print("second_diff_ratio:", "%.4f" % second_diff_ratio)

        third_diff_ratio = abs(first_duration_mean_power_of_max_freq - third_duration_mean_power_of_max_freq) / first_duration_mean_power_of_max_freq
        if third_diff_ratio < 0.1:
            exit_code_third = 1
        else:
            exit_code_third = 2
        print("third_diff_ratio:", "%.4f" % third_diff_ratio)
    else:
        print("The number of audio section should equal 3.")


def process_argv():
    parser = argparse.ArgumentParser(prog='silence_detect')
    parser.add_argument('--file', '-f', help='The path of the audio file.', required=True)
    # parser.add_argument('--allSingleFreq', '-a', help='If the audio is all single frequency.', choices=['true', 'false'], default='true')
    return parser.parse_args()


if __name__ == '__main__':
    arg = process_argv()
    sample_rate, signal = scipy.io.wavfile.read(arg.file)
    # sample_rate, signal = scipy.io.wavfile.read(r"D:\cats\bugs\1812\400-800-1200-1600.wav")
    # pow_spec = calc_stft(signal, sample_rate, NFFT=sample_rate)
    pow_spec = calc_stft(signal, sample_rate)
    # if arg.allSingleFreq == 'true':
    #     result = detect_mix_for_audio_only_with_single_freq(pow_spec)
    # else:
    #     result = detect_mix_for_audio_with_single_and_multi_freq(pow_spec)
    result, max_freq = detect_mix_for_audio_with_single_and_multi_freq(pow_spec)
    print('The index and start-end time:')
    for key, value in result.items():
        print(str(key) + ' : ' + "%.2f" % (value[0] * frame_stride) + " - " + "%.2f" % (value[1] * frame_stride))
    analyze_every_section(pow_spec, result, max_freq)
    exit(int(str(exit_code_first) + str(exit_code_second) + str(exit_code_third)))
