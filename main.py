import os
import cv2
from app import app
from flask import Flask, flash, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
from configs.default import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS

from engine import detect_whiteboard, detect_text, init_text_detector

global reader
reader = init_text_detector()

def allowed_file(filename, category):
	if category == 'image':
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
	elif category=='video':
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def process_input(filename):
	img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'],filename))
	boards, wb_img = detect_whiteboard(img)
	cv2.imwrite(os.path.join(app.config['RESULT_FOLDER'],filename),wb_img)
	results = detect_text(boards, reader)
	final_res_string = ''
	for i, res in enumerate(results):
		final_res_string += f' Whiteboard {(i+1)}: '.join(res)
	return final_res_string

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/image', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename, 'image'):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		results = process_input(filename)
		flash('Image successfully uploaded and displayed below')
		return render_template('image.html', filename=filename, results=results)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/video',methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename, 'video'):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		flash('Video successfully uploaded and displayed below')
		return render_template('video.html', filename=filename)
	else:
		flash('Allowed video types are -> webm, mp4, avi, mov')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_input(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/output/<filename>')
def display_output(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='results/' + filename), code=301)

# @app.route('/video_feed')
# def video_feed():
# 	# return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
	

@app.route('/video-feed')
def gen_frames():  
	camera = cv2.VideoCapture(1)
	while True:
		success, frame = camera.read() 
		print(success) # read the camera frame
		if not success:
			break
		else:
			_, buffer = cv2.imencode('.jpg', frame)
			frame = buffer.tobytes()
			return Response ((b'--frame\r\n' 
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'), 
				   mimetype='multipart/x-mixed-replace; boundary=frame') # concat frame one by one and show result
	

if __name__ == "__main__":
	app.run()