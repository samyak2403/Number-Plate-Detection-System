# Number Plate Detection System

## Overview

This project is a Number Plate Detection System implemented with a graphical user interface (GUI) using Python. It processes video and image inputs to detect and recognize vehicle number plates, mapping them to specific Indian states and districts using a simplified state mapping system.

## Features

- **Video and Image Processing:**
  - Load videos or images for number plate detection.
  - Real-time video playback with detection overlay.

- **Detection Methods:**
  - Utilizes Haar Cascade Classifier, contour-based methods, and edge detection to identify number plates.

- **Mapping to Regions:**
  - Identifies the state and district based on Indian vehicle registration codes.

## Installation

1. Make sure to have Python installed.
2. Install the required dependencies:
   ```
   pip install opencv-python-headless pillow
   ```

## Usage

1. Run the main application:
   ```
   python main.py
   ```
2. Use the GUI to upload a video or image for processing.

## Files

- `main.py`: The main application with the GUI.
- `plate_detector.py`: Contains the detection logic and methods.
- `state_mapper.py`: Maps registration codes to states and districts.

## License

This project is licensed under the MIT License.
