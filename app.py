from flask import Flask,render_template,request,redirect,send_from_directory, url_for
from PyPDF2 import PdfFileReader, PdfFileWriter,PdfFileMerger
import os,sys,glob
from pathlib import Path
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'pdf'}
    
app = Flask(__name__)
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

def merge_pdfs(pdf_list,filename):
    merger = PdfFileMerger()
    for pdf in pdf_list:
        #print(pdf)
        if allowed_file(pdf.filename) and secure_filename(pdf.filename):
            merger.append(pdf)
    merger.write("downloads/"+filename+".pdf")
    if(filename == mailid):
        filename=filename+".pdf"
        return redirect(url_for('uploaded_file', filename=filename))  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(file_path,wm_path, filename,watermark):
    add_watermark(file_path,wm_path ,filename,watermark)

def add_watermark(file_path,wm_path,filename,watermark):
    template = PdfFileReader(open(file_path,'rb'))
    watermark = PdfFileReader(open(wm_path,'rb'))

    output = PdfFileWriter()

    for i in range(template.getNumPages()):
        page = template.getPage(i)
        page.mergePage(watermark.getPage(0))
        output.addPage(page)
    output_stream = open(app.config['DOWNLOAD_FOLDER'] + filename, 'wb')
    output.write(output_stream)

def clear_directories():
    l=["uploads","downloads"]
    for i in l:
        mypath = i
        for root,dirs,files in os.walk(mypath):
            for file in files:
                os.remove(os.path.join(root, file))
    #print("cleared dirs!")
def write_to_file(email_id):
    database = open('static/database.txt','a')
    email = email_id
    file = database.write(f'\n{email}')
    database.close()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        data=request.form.to_dict()
        if data['option']=="merge":
            try:
                #print(len(request.files.getlist('file')))
                if len(request.files.getlist('file'))<=1:
                    print('No file attached in request')
                    return redirect('/')
                #elif 'file' in request.files.getlist('file'):
                elif len(request.files.getlist('file'))>1:
                    clear_directories()
                    global mailid
                    write_to_file(data['mail'])
                    mailid=data['mail'].rsplit('@', 1)[0].lower()
                    #print(mailid)
                    return merge_pdfs(request.files.getlist('file'),mailid)
            except:
                return "Did not merge. Try again"
        elif data['option']=="wm":
            if 'file' not in request.files and 'wm_file' not in request.files:
                print('No file attached in request')
                return redirect('/')
            file = request.files['file']
            wm_file = request.files['wm_file']
            if file.filename == '' and wm_file.filename=='':
                print('No file selected')
                #return redirect(request.url)
                return redirect('/')
            if file and allowed_file(file.filename) and allowed_file(wm_file.filename):
                filename = secure_filename(file.filename)
                watermark = secure_filename(wm_file.filename)
                clear_directories()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                wm_file.save(os.path.join(app.config['UPLOAD_FOLDER'], watermark))
                process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),os.path.join(app.config['UPLOAD_FOLDER'], watermark), filename,watermark)
                return redirect(url_for('uploaded_file', filename=filename))  
    return render_template('index.html')

@app.route('/ok')
def ok():
    return render_template('ok.html')
