# Whiteboard Text Detection

This repository runs a python app to detect text from the uploaded images. The future updates will include reading text from videos or webcam. 

[](screenshots/home.png)


Result of the uploaded image will have the detected whiteboard and text as shown below.

[](screenshots/result.png)

## Technical breakdown

This is a flask app that uses OpenCV shape detector to find out whiteboards and for each whiteboard (or rectangle) found it detects the text using the [EasyOCR](https://github.com/JaidedAI/EasyOCR) library.

### Setup

To install the dependencies for the app, 

```bash
sh setup.sh
```

Note: For EasyOCR, please install torch and torchvision first by following the official instructions [here](https://pytorch.org). On the pytorch website, be sure to select the right CUDA version you have. If you intend to run on CPU mode only, select CUDA = None.
