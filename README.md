# Screenburst

A small Python GUI that takes a series of screenshots at a set interval.

## Features
- Choose the number of screenshots, delay between them, and save folder
- Start / Stop buttons
- Keeps capturing if you close the window, then exits when done

## Usage
```bash
pip install pillow
python screenshot_series.py
```

Works on Windows and macOS (grant Screen Recording permission on macOS). On Linux it needs X11.
