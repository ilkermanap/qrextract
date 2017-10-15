import os
from flask import Flask, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
import zbar
import Image

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and  filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class QRReader:
    def __init__(self, fname):
        sc = zbar.ImageScanner()
        pil = Image.open(fname).convert("L")
        raw = pil.tobytes()
        w,h = pil.size
        self.img = zbar.Image(w,h,'Y800', raw)
        sc.scan(self.img)
        
    def __str__(self):
        cev = "<htm><pre>"
        for s in self.img:
            t = ""
            for x,y in s.location:
                t += "(%d, %d) " % (x,y)
            cev += t + " : " + s.data + " \n"
        return cev + "</pre></html>"

    def json(self):
        res = {}
        i = 0
        for s in self.img:
            print dir(s)
            res[i] = {"data": s.data, "location": (s.location[0], s.location[2]),
                          "count": s.count, "quality": s.quality, "type": "%s" % s.type, }
            i += 1            
        return jsonify(res)

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
            d = QRReader(f)
            outtype = request.form.get("outtype")
            if outtype == "json":
                return d.json()
            elif outtype == "html":
                return str(d)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <p><input type=radio name=outtype value="json" checked>JSON
      <p><input type=radio name=outtype value="html" ">HTML
      <p><input type=text name=deneme value="denemedir">
      <p><input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002,  debug=True)
