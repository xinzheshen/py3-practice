# Code to execute in an independent thread
import time
def countdown(n):
    while n > 0:
        print('T-minus', n)
        n -= 1
        time.sleep(1)

# Create and launch a thread
from threading import Thread
t = Thread(target=countdown, args=(5,))
# t.setDaemon(True)
t.start()

# t.join()
print("end")