#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

import numpy as np
import scipy.io.wavfile
from collections import OrderedDict
import sys
import time
import argparse
import librosa


# whether the audio file has sound, yes(1), no(2)
exit_code_first = 2
# whether the sound changes to mute(1) , slowly_down(2), not_change(3)
exit_code_second = 0
# whether the audio file has silence because of "Dwell time" after chime, yes(1), no(2)
exit_code_third = 2
# whether the sound recovers back after mute or slowly down, yes(1), no(2)
exit_code_fourth = 0

frame_size = 0.025
frame_stride = 0.01
frame_length = 0
frame_step = 0
sample_rate = 0

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


def detect_mix_for_audio_with_single_and_multi_freq(pow_spec, sample_rate):
    print("Detecting sections...")
    global exit_code_first
    result = OrderedDict()
    start = 0
    number = 0
    flag = True
    new_section = True
    multi_freq_section = False
    max_valid_freq = 0
    current_section_is_single = True

    # hard code
    base_power = 5000
    base_power_scale = 0.0001
    if sample_rate == 16000:
        freq_scope = int(n_fft / 4)
        single_freq_threshold = 400
    else:
        freq_scope = int(n_fft / 8)
        single_freq_threshold = 150

    for index, powers in enumerate(pow_spec):
        max_power_freq_index = np.argmax(powers)
        max_power = powers[max_power_freq_index]

        # Normally the power should be bigger than base_power when there is voice
        if max_power > base_power:
            max_valid_freq = max_valid_freq if (max_valid_freq > max_power_freq_index) else max_power_freq_index
            exit_code_first = 1
            condition = base_power if base_power > max_power * base_power_scale else max_power * base_power_scale
            valid_frequencies = np.where(powers > condition)
            max_freq = max(valid_frequencies[0])
            min_freq = min(valid_frequencies[0])

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
                    # if last_result[1] - last_result[0] > 15:
                    number += 1
                    start = index
                    current_section_is_single = not last_result[2]

            result[number] = [start, index, current_section_is_single]
    return result, max_valid_freq


def analyze_every_section(pow_spec, result, max_freq):
    global exit_code_second, exit_code_third, exit_code_fourth
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
        # print("second_first_diff_ratio:", "%.4f" % second_diff_ratio)

        third_diff_ratio = abs(first_duration_mean_power_of_max_freq - third_duration_mean_power_of_max_freq) / first_duration_mean_power_of_max_freq
        if third_diff_ratio < 0.1:
            exit_code_fourth = 1
        else:
            exit_code_fourth = 2
        # print("third__first_diff_ratio:", "%.4f" % third_diff_ratio)

        if third_duration[0] - second_duration[1] != 1:
            exit_code_third = 1

        normalize_audio(pow_spec[second_duration[0]: second_duration[1], :])
    else:
        print("The number of audio section should equal 3.")


def merge_short_duration_in_result(result):
    number = 1
    # Sometimes there is silence in chime, assume the silence is less than 15（0.15 second）
    duration_threshold = 15
    final_result = OrderedDict()
    for key, value in result.items():
        if key > 1:
            if value[1] - value[0] < duration_threshold and result[key - 1][1] - result[key - 1][0] < duration_threshold:
                number = list(final_result.keys())[-1]
                final_result[number] = (final_result[number][0], value[1], final_result[number][2])
            else:
                number += 1
                final_result[number] = value
        else:
            final_result[number] = value

    return final_result


def normalize_audio(data):
    global frame_length, frame_step
    frequency_threshold = 200
    # data[:, frequency_threshold:] = 0
    print("here")
    tmp = librosa.istft(data, hop_length=frame_step, win_length=frame_length, dtype=np.float64)
    out = r"D:\cats\audios\chimes\615_715\real\tmp.wav"

    librosa.output.write_wav(out, tmp, sr=sample_rate)
    import noisereduce as nr

    # noisy_part = signal[:10000].astype(np.float32)
    # reduced_noise = nr.reduce_noise(audio_clip=signal.astype(np.float32), noise_clip=noisy_part)
    #

def process_argv():
    parser = argparse.ArgumentParser(prog='detect_mix')
    parser.add_argument('--file', '-f', help='The path of the audio file.', required=True)
    return parser.parse_args()


def main():
    global frame_step, frame_length, sample_rate
    arg = process_argv()
    sample_rate, signal = scipy.io.wavfile.read(arg.file)

    # sig, rate = librosa.load(arg.file, sr=16000)
    tmp = np.fft.fft(signal)
    tmp2 = np.fft.ifft(tmp)
    out = r"D:\cats\audios\chimes\615_715\real\tmp.wav"
    tmp3 = np.around(np.abs(tmp2), decimals=0, out=None).astype(np.int)
    tmp3[::2] *= -1
    tmp4 = np.real(tmp2).astype(np.int)
    scipy.io.wavfile.write(out, sample_rate, tmp3)
    # librosa.output.write_wav(out, tmp2, sr=sample_rate)

    # frame_length = int(frame_size * rate)

    import matplotlib.pyplot as plt
    xf=tmp/len(signal)
    lens = len(signal)
    freqs = np.linspace(0, sample_rate/2, len(signal)/2+1)
    plt.figure(figsize=(16,4))
    plt.plot(2*np.abs(xf), 'r--')

    plt.xlabel("Frequency(Hz)")
    plt.ylabel("Amplitude($m$)")
    plt.title("Amplitude-Frequency curve")

    plt.show()


    frame_step = int(frame_stride * rate)
    result_stft = librosa.stft(sig, n_fft=1024, hop_length=frame_step, win_length=frame_length, dtype=np.float64)
    # result_stft = result_stft.reshape(result_stft.shape[1], -1)
    pow_spec = calc_stft(signal, sample_rate)
    # pow_spec = result_stft

    normalize_audio(result_stft)

    # librosa.fft_frequencies()
    result, max_freq = detect_mix_for_audio_with_single_and_multi_freq(pow_spec, sample_rate)
    # for key, value in result.items():
    #     print(str(key) + ' : ' + "%.2f" % (value[0] * frame_stride) + " - " + "%.2f" % (value[1] * frame_stride))
    final_result = merge_short_duration_in_result(result)
    print('The index and start time - end time:')
    for key, value in final_result.items():
        print(str(key) + ' : ' + "%.2f" % (value[0] * frame_stride) + " - " + "%.2f" % (value[1] * frame_stride))
    analyze_every_section(pow_spec, final_result, max_freq)

    exit(int(str(exit_code_first) + str(exit_code_second) + str(exit_code_third) + str(exit_code_fourth)))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
        exit(-1)
