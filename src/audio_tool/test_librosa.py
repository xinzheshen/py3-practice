import librosa

# y, sr = librosa.load(librosa.util.example_audio_file(), offset=30, duration=2.0)
y, sr = librosa.load(r"D:\cats\audios\chimes\615_715\audio_with_615.wav")
onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
print(librosa.frames_to_time(onset_frames, sr=sr))


def detect_mix_for_audio_with_single_and_multi_freq(pow_spec):
    result = OrderedDict()

    start_time = 0
    number = 0
    multi_freq = True
    new_section = True
    max_valid_freq = 0
    for index_time, powers in enumerate(pow_spec):
        index_time = index_time/100.0
        max_power_freq_index = np.argmax(powers)
        max_power = powers[max_power_freq_index]
        max_valid_freq = max_valid_freq if (max_valid_freq > max_power_freq_index) else max_power_freq_index
        # Normally the power should be bigger than 5000 when there is voice
        if max_power > 5000:
            valid_frequencies = np.where(powers > 5000)
            max_freq = max(valid_frequencies[0])
            min_freq = min(valid_frequencies[0])

            if index_time == 7.08:
                print(max_freq, min_freq)
            if (max_freq - min_freq) < 200:
                # 是同一段音频
                if multi_freq:
                    multi_freq = False
                    new_section = True
                if new_section:
                    new_section = False
                    multi_freq = False
                    # number += 1
                    if number == 0:
                        number += 1
                        start_time = index_time
                    else:
                        last_duration = result[number].split("-")
                        if float(last_duration[1]) - float(last_duration[0]) > 0.1:
                            number += 1
                            start_time = index_time
            else:
                if not multi_freq:
                    multi_freq = True
                    new_section = True
                if new_section:
                    new_section = False
                    # start_time = index_time
                    if number == 0:
                        number += 1
                        start_time = index_time
                    else:
                        last_duration = result[number].split("-")
                        if float(last_duration[1]) - float(last_duration[0]) > 0.1:
                            number += 1
                            start_time = index_time

            duration = str(start_time) + '-' + str(index_time)

            result[number] = duration

    return result


def detect_mix_for_audio_with_single_and_multi_freq(pow_spec):
    global exit_code_first
    result = OrderedDict()
    start = 0
    number = 0
    flag = True
    new_section = True
    multi_freq_section = 0
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

            # judge the valid freq scope
            if (max_freq - min_freq) < freq_scope:
                # It says it's the same audio
                if flag:
                    flag = False
                    new_section = True
            else:
                if not flag:
                    flag = True
                    new_section = True
            if new_section:
                new_section = False
                if number == 0:
                    number += 1
                    start = index
                    if max_power_freq_index < single_freq_threshold:
                        current_section_is_single = False
                else:
                    last_duration = result[number]
                    # Sometimes there is silence in chime, assume the silence is less than 10（0.1 second）
                    if last_duration[1] - last_duration[0] > 10:
                        number += 1
                        start = index

            result[number] = (start, index)
    return result, max_valid_freq