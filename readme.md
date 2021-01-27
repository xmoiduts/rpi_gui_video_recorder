# Raspberry PI video recorder with VNC-visible previews.

Though `raspivid` on Raspberry PI records videos, its preview window is invisible in VNC remote sessions as whey were laid on the hardware video output signal. However display (monitors) are sometimes inaccessible on the video-recording site where preview may also be needed.

This script calls OpenCV that draws preview on RPI's GUI desktops, meaning that it's visible via VNC sessions. During the preview, several parameters can be adjusted by keyboard inputs in real time, those changes also take effect immediately on the recorded videos. 

# Dependencies:

- OpenCV (the pip installed one is enough)
- picamera
- RPI's Desktop environment (Optionally, if you want preview)

## Usage:

`python3 video_recorder.py -O <video_filename> [optional parameters] `

By default it discards recorded videos, to save videos at least an output filename is needed.

### Example:

`python3 video_recorder.py -O todaysVideo`

## Optional Parameters:

-md --sensor_mode int 2 pi camera mode

| parameter | alias(?)         | data type | default     | note                                                         |
| --------- | ---------------- | --------- | ----------- | ------------------------------------------------------------ |
| -md       | --sensor_mode    | int       | 2           | Pi Camera mode, see [picamera docs](https://picamera.readthedocs.io/en/latest/fov.html#sensor-modes) |
| -W        | --width          | int       | 1920        | Width of recorded video[s]                                   |
| -H        | --height         | int       | 1080        | Height of recorded video[s]                                  |
| -F        | --fps            | int       | 10          | Video framerate, see [picamera docs](https://picamera.readthedocs.io/en/latest/fov.html#sensor-modes) |
| -O        | --output         | str       | /dev/null   | Filename[s] for the recorded video[s], don't add filename extensions like '.mp4'/'.h264', segment suffixes will be added automatically |
|           | --hf             |           | \<not use\> | Add this flag to enable: Flip the video horizontally         |
|           | --vf             |           | \<not use\> | Add this flag to enable: Flip the video vertically           |
|           | --no-preview     |           | \<not use\> | Add this flag to disable preview; Desktop GUI environment is required for enabling preview. |
| -t        | --time-length    | int       | 1200        | Length of the entire record in seconds, the script supports up to 1000 segments. |
| -sg       | --segment-length | int       | 300         | (Rough) length of each video segment in seconds, segmentation can only be done on a key frame, which happens every several seconds. |
| -b        | --bitrate        | float     | 5           | Video bitrate Mbps                                           |

## Keyboard actions:

| key input, case sensitive | action                                                       |
| ------------------------- | ------------------------------------------------------------ |
| q                         | Close OpenCV-based preview windows while not terminating recording |
| l                         | Increase preview framerates,  min ~0.5fps and max < 20 fps   |
| h                         | Decrease preview framerates, high preview framerates consumes high CPU. |
| j                         | Downscale preview window size (width), 6 widths [240, 320, 480, 640, 800, 1024] are provided. |
| k                         | Upscale preview window size                                  |
| b                         | Toggle `backlight` mode, enable this in high lighting contrast cases and see the perceived video quality in preview windows. |
| a                         | Increase exposure compensation  by 1 (which is between -25~+25) |
| s                         | Reset exposure compensation  to 0                            |
| d                         | Decrease exposure compensation  by 1                         |
| ctrl+c                    | Exit script, record videos  should have been saved by it.    |