import win32api
import win32gui

WM_APPCOMMAND = 0x319

APPCOMMAND_VOLUME_MAX = 0x0a
APPCOMMAND_VOLUME_MIN = 0x09
tmp = APPCOMMAND_VOLUME_MAX * 0x10000
tmp2 = 0x30292
#音量最大
result = win32api.SendMessage(-1, WM_APPCOMMAND, 0x30292, 26 * 0x10000)

#音量最小
# win32api.SendMessage(-1, WM_APPCOMMAND, 0x30292, APPCOMMAND_VOLUME_MIN * 0x10000)

tmp3 = 26 * 0x10000
tmp4 = 26 << 16


# 从顶层窗口向下搜索主窗口，无法搜索子窗口
# FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名
handle = win32gui.FindWindow("Notepad", None)


# 获取窗口位置
left, top, right, bottom = win32gui.GetWindowRect(handle)
#获取某个句柄的类名和标题
title = win32gui.GetWindowText(handle)
clsname = win32gui.GetClassName(handle)

# 打印句柄
# 十进制
print(handle)
# 十六进制
print("%x" %(handle) )

print('end')

