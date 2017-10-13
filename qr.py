import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import zbar
import Image

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and  filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_qr(fname):
    sc = zbar.ImageScanner()
    pil = Image.open(fname).convert("L")
    raw = pil.tostring()
    w,h = pil.size
    img = zbar.Image(w,h,'Y800', raw)
    sc.scan(img)

    cev = "<htm><pre>"
    for s in img:
        t = ""
        for x,y in s.location:
            t += "(%d, %d) " % (x,y)
        cev += t + " : " + s.data + " \n"
        
    return cev + "</pre></html>"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(f)
            return extract_qr(f)
            #return redirect(url_for('uploaded_file',
            #                        filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002,  debug=True)

#QRCODE ((683, 196), (683, 429), (917, 430), (916, 196))
#QRCODE ((84, 136), (84, 580), (528, 580), (529, 136))

