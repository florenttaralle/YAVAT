# YAVAT - Yet Another Video Annotation Tool

![](assets/Screenshot.png)

Yet Another Video Annotation Tool meant to be easy to use. 
Make video event annotations fast and easy.

It focusses on simple time events only; not boxes, segmentation, ... 
An event is defined by a start a stop and optionaly a string label.
Start and stop of events can only be on an exact frame timestamp.
An event can be ponctual: one-frame wide. 

Implementation in Python3. It uses PyQt6 and ffmpeg.

## Features

- Create/Name/Delete Annotation Timelines.
- Create/Label/Delete Events on a timeline.
- Save/Load Annotations in a JSON-based YAVAT File.
- Show named timeseries stored in the annotation file.

## TODO / Suggestions

- Implement moving event to another timeline.
- Implement Annotation Grid (like in ELAN)
- Import timeseries from CSV file.
- Delete timeseries.

## Getting Started

### Installation 

``` shell
pip3 install -r requirements.txt

sudo apt install qtmultimedia
sudo apt install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav
```

### Launching the App

``` shell
usage: yavat.py [-h] [-l LABELS_PATH] [-t TIMELINE] video_path

positional arguments:
  video_path

options:
  -h, --help            show this help message and exit
  -l LABELS_PATH, --labels_path LABELS_PATH
  -t TIMELINE, --timeline TIMELINE
```

## Application Shortcuts

UX has been designed to ensure that annotation experience is as fast and pleasant as possible.
Shortcuts are provided to allow keyboard-only annotation.
I use this tool a lot myself.


### Anytime

- `M`:                      Mute/Unmute video.
- `Space`:                  Play/Pause
- `RightArrow`:             Move Forward 1 second
- `LeftArrow`:              Move Backward 1 second
- `Ctrl + RightArrow`:      Move Forward 1 frame
- `Ctrl + LeftArrow`:       Move Backward 1 frame
- `UpArrow`:                Select previous timeline
- `DownArrow`:              Select next timeline
- `Ctrl`:                   Hide event handles (handy to move a ponctual event).
- `Shift + RightArrow`      Move to the next event boundary on the selected timeline.
- `Shift + LeftArrow`       Move to the previous event boundary on the selected timeline.

### When no Event on the selected timeline at the current time position

- `E`:                          Add an Event starting at current time position
- `Ctrl + Shift + RightArrow`:  Move the right boundary of the nearest previous event forward to the current time position.
- `Ctrl + Shift + LeftArrow`:   Move the left boundary of the nearest next event backward to the current time position.

### When a Range Event is active on the selected timeline

- `Delete`:                     Delete the event.
- `Ctrl + Shift + LeftArrow`:   Move the left boundary of the event forward to the current time position.
- `Ctrl + Shift + RightArrow`:  Move the right boundary of the event backward to the current time position.

## About Timeseries

Timeseries are simple 2D line plots. The objective here is not to allow editing them but to show graphs synchronised with the timelines.
At the moment, the only way to add timeseries is to inject them in the annotation file (manualy or programmatically).

``` json
{
  "video": { ... },
  "timelines": [...], 
  "timeseries": [
    {
      "name":       "Timeseries Name",
      "y_min":      0.0,
      "y_max":      1.0,
      "xy_values":  [[x0, y0], [x1, y1], ..., [xn, yn]]
    }
  ]
}
```



# Contributing

I welcome contributions from other developers to help me make this application even better.

## Credits

This project is inspired by the tools I used or have tested. 

- [ANVIL](http://www.anvil-software.de/)
- [VIA Annotator](https://www.robots.ox.ac.uk/~vgg/software/via/app/via_video_annotator.html)
- [ELAN](https://archive.mpi.nl/tla/elan)

## License

Copyright (c) 2024 Florent TARALLE, YAVAT is released under the MIT license.
