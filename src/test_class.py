
print("tets_class")
class testClass(object):
    def __new__(cls, *args, **kwargs):
        print("new...")
        return object.__new__(cls)

    def __init__(self):
        print("init...")


import os
from os.path import join, getsize
for root, dirs, files in os.walk('python/Lib/email'):
    print(root, "consumes", end="")
    print(sum([getsize(join(root, name)) for name in files]), end="")
    print("bytes in", len(files), "non-directory files")
    if 'CVS' in dirs:
        dirs.remove('CVS')  # don't visit CVS directories