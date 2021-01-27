# -*- coding: UTF-8 -*-

# Generate file name
def fileNameGenerator(filename: str, ext = '.h264'):
    # do not process /dev/null otherwise /dev/null_0001.h264 -> 'permission denied'.
    if filename == '/dev/null':
        while True:
            yield '/dev/null'
    else:
        for curr in range(1000):
            yield '{}_{:03d}{}'.format(filename, curr, ext)
