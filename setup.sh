#!/bin/bash

# installing env
pip install easyocr

## uninstalling to avoid opencv imshow issues
pip uninstall opencv-python-headless -y 
pip uninstall opencv-python -y 
pip install -r requirements.txt