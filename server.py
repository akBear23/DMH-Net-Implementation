from flask import Flask, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from flask import render_template, make_response
from flask import send_from_directory
from PIL import Image
import json


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, template_folder='client')
app.config['UPLOAD_FOLDER'] = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with Image.open(filepath) as img:
                img = img.resize((1024, 512))
                img.save(filepath)
            return render_template('app.html', filename=filename)
    return render_template('app.html')
@app.route('/uploads/<filename>')
def send_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/label/<filename>')
def label_image(filename):
    # Generate the URL for the image
    image_url = url_for('send_file', filename=filename)
    # Render a template that includes the label tool and the image
    return render_template('label.html', image_url=image_url)

@app.route('/save_point', methods=['POST'])
def save_point():
    # Get the coordinates from the request
    data = request.get_json()
    coordinates = data['coordinates']
    print(coordinates)
    # Save the coordinates to a database or a file
    with open('coordinates.txt', 'a') as f:
        tmp = json.dumps(coordinates) 
        split_list = list(tmp)
        split_list = [char for char in tmp if char not in [' ']]
        # f.write(split_list)
        x = ''.join(split_list[1:split_list.index(',')])
        y = ''.join(split_list[split_list.index(',')+2:-1])
        f.write(x + ' ' + y + '\n')
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
