# -*- coding: UTF-8 -*-

#import numpy as np 
#import imutils
import cv2
import picamera
import argparse
import threading
import time
#from util.fname_gen import fileNameGenerator 

# Handle argument
ap = argparse.ArgumentParser()
ap.add_argument('-md', '--sensor_mode', type = int, default=2, help = 'Pi camera mode') # see picamera docs
ap.add_argument('-W', '--width', type = int, default=1920, help = 'Width of recorded video')
ap.add_argument('-H', '--height', type = int, default=1080, help = 'Height of recorded video')
ap.add_argument('-F', '--fps', type = int, default=10, help = 'Video framerate')
ap.add_argument('-O', '--output', type = str, default='/dev/null', help = 'Specify the filename[s] you want to store the video[, segment suffixes will be added automatically].')
ap.add_argument('--hf', action='store_true', help = 'horizontally flip the video')
ap.add_argument('--vf', action='store_true', help = 'vertically flip the video')
ap.add_argument('--no-preview', dest = 'preview', default=True, action = 'store_false', help = 'Show preview window, needs desktop environment')
ap.add_argument('-t', '--time_length', type = int, default=1200, help = 'Length of the entire record in seconds')
ap.add_argument('-sg', '--segment_length', type = int, default=300, help = 'Length of each video segment in seconds')
ap.add_argument('-b', '--bitrate', type = float, default=5, help = 'Video bitrate Mbps')
args = vars(ap.parse_args()) 
print(args) 


# Generate file name
def fileNameGenerator(filename: str, ext = '.h264'):
    # do not process /dev/null otherwise /dev/null_001.h264 -> 'permission denied'.
    # other filenames: 'aaa' -> 'aaa_001.h264', ...
    if filename == '/dev/null':
        while True:
            yield '/dev/null'
    else:
        for curr in range(1000):
            yield '{}_{:03d}{}'.format(filename, curr, ext)

'''protector22'''

def windowed_preview(camera,w,h):
    from picamera.array import PiRGBArray 
    size = [240, 320, 480, 640, 800, 1024]
    grade = 2 
    aspect_ratio = h/w
    rawCapture = PiRGBArray(camera, size=(size[grade], int(size[grade]*aspect_ratio)))
    # Control interval refreshing rate
    interval = [0.05, 0.07, 0.1, 0.14, 0.2, 0.4, 0.5, 1, 2]
    level = 4
    global preview_stop, preview_pause

    while True:
        if preview_stop == True:
            print('[Preview]-Quiting')
            break
        if preview_pause == True:
            time.sleep(0.1)
        camera.capture(rawCapture, format = 'bgr', resize = (size[grade], int(size[grade]*aspect_ratio)), use_video_port = True)
        cv2.imshow('Preview', rawCapture.array)
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        time.sleep(interval[level])

        if key == ord('q'):
            cv2.destroyWindow('Preview')
            print('[Preview] Window Closed, recording continues')
            break
        elif key == ord('l'): # Update preview faster to increase smoothness
            level = 0 if level == 0 else level - 1
            print('[Preview]-Frame interval: {}s'.format(interval[level]))
            continue
        elif key == ord('h'): # Update preview slower to reduce cpu workload
            level = len(interval) - 1 if level == len(interval) - 1 else level + 1
            print('[Preview]-Frame interval: {}s'.format(interval[level]))
            continue
        elif key == ord('j'): # Downscale preview window
            grade = 0 if grade == 0 else grade - 1 
            print('[Preview]-Downscaled to: {} * {}'.format(size[grade], int(size[grade]*aspect_ratio)))
            rawCapture = PiRGBArray(camera, size=(size[grade], int(size[grade]*aspect_ratio)))
            continue
        elif key == ord('k'): # Upscale preview window 
            grade = len(size) - 1 if grade == len(size) - 1 else grade + 1
            print('[Preview]-Upscaled to: {} * {}'.format(size[grade], int(size[grade]*aspect_ratio)))
            rawCapture = PiRGBArray(camera, size=(size[grade], int(size[grade]*aspect_ratio)))
            continue
        elif key == ord('b'): # toggle backlight
            camera.exposure_mode = 'auto' if camera.exposure_mode == 'backlight' else 'backlight'
            print('[Preview]-exposure_mode toggled to {}'.format(camera.exposure_mode))
            continue
        elif key == ord('a'): # exposure compensation +
            if camera.exposure_compensation < 25:
                camera.exposure_compensation += 1
            print('[Preview]-EV added to {}'.format(camera.exposure_compensation))
            continue
        elif key == ord('s'): # exposure compensation reset to 0
            camera.exposure_compensation = 0
            print('[Preview]-EV subed to {}'.format(camera.exposure_compensation))
        elif key == ord('d'): # exposure compensation -
            if camera.exposure_compensation > -25:
                camera.exposure_compensation -= 1
            print('[Preview]-EV subed to {}'.format(camera.exposure_compensation))
            continue

    return

# Init Camera
fg = fileNameGenerator(args['output'], '.h264')
with picamera.PiCamera(framerate = args['fps'], sensor_mode = args['sensor_mode']) as camera:
    camera.resolution = (args['width'], args['height'])
    if args['hf'] == True:
        camera.hflip = True
    if args['vf'] == True:
        camera.vflip = True
    total_segments = args['time_length'] // args['segment_length'] + 1 #BUG: split_recording() will wait for the next I-frame to come, making each segment longer than specified, but total segments don't reduce accordingly, causing total vedio duration longer.
    camera.start_recording(next(fg), format = 'h264', bitrate = int(args['bitrate'] * 1000000))
    camera.wait_recording(1)

    if args['preview'] == True:
        preview_stop = False
        preview_pause = False
        pr = threading.Thread(target = windowed_preview, args = (camera, args['width'], args['height']))
        pr.daemon = True
        pr.start()

    try: 
        for segment in range(total_segments):
            camera.wait_recording(args['segment_length'] - 0.2)
            #preview_pause = True
            #camera.wait_recording(0.2)
            camera.split_recording(next(fg)) #https://github.com/waveform80/picamera/issues/49   split after capture causes error
            #TODO log the split aciton
            #preview_pause = False
        print('[INFO]-Finished recoding all segments')
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        print('\n[INFO]-Bye')
    finally:
        if args['preview'] == True:
            preview_stop = True
            time.sleep(3)
            pr.join(4)
        camera.stop_recording()
        print('[INFO]-Program Quitting')

    