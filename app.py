from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64
from io import BytesIO
from PIL import Image
from model import Model
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
model = Model('./models/super-resolution-10.onnx')

@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html')

def decode_image(base64_data):
    try:
        header, encoded = base64_data.split(",", 1)
        data = base64.b64decode(encoded)
        image = Image.open(BytesIO(data))
        return image
    except Exception as e:
        logging.error(f"Failed to decode image: {e}")
        return None

def image_to_base64(img):
    try:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logging.error(f"Failed to convert image to base64: {e}")
        return None

@socketio.on('send_frame')
def handle_frame(data):
    try:
        frame_data = data['frame']
        image = decode_image(frame_data)
        if image is not None:
            processed_image = model.process_image(image)
            image_base64 = image_to_base64(processed_image)
            emit('frame_response', {'image': image_base64})
        else:
            emit('error', {'error': 'Failed to decode image'})
    except Exception as e:
        logging.error(f"Error processing frame: {e}")
        emit('error', {'error': 'Error processing image'})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
