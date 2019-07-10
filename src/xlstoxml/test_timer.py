import threading

def func():
    print('hello timer!')

timer = threading.Timer(1, func)
timer.start()
print("end")