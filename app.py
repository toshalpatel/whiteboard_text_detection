'''
source: https://roytuts.com/upload-and-display-image-using-python-flask/
'''

from flask import Flask
from configs.default import UPLOAD_FOLDER, RESULT_FOLDER, max_content_len

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = max_content_len