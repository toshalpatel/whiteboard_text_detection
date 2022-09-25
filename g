# Whiteboard Text Detection

This repository runs a python app to detect text from the uploaded images. The future updates will include reading text from videos or webcam. 

()[screenshots/home.png]


Result of the uploaded image will have the detected whiteboard and text as shown below.

()[screenshots/result.png]

## Setup

Run
'''bash
sh setup.sh
'''

EasyOCR requires pytorch implementation, hence, you can install the gpu version, otherwise by default the setup script will install the cpu version and run the inference.