import ctypes
import clr
import sys
# ctypes 加载 C/C++ 的dll
# dll = ctypes.WinDLL('./DLL/AudioSwitcher.AudioApi.CoreAudio.dll')
# dll = ctypes.WinDLL('./DLL/AudioSwitcher.AudioApi.CoreAudio.dll')

sys.path.append("./DLL")
# 加载c# dll文件
clr.FindAssembly("AudioSwitcher.AudioApi.CoreAudio.dll")

from AudioSwitcher.AudioApi.CoreAudio import CoreAudioController    # 导入命名空间
# create object
audio_ctrl_obj = CoreAudioController()
mic_device = audio_ctrl_obj.DefaultCaptureDevice
if mic_device:
    print("current mic volume is " + str(mic_device.Volume))
    mic_device.Volume = 80
else:
    print('there is not mic device.')

speaker_device = audio_ctrl_obj.DefaultPlaybackDevice
print("current speaker volume is " + str(speaker_device.Volume))
print('end')

