from flask import Flask,render_template,request,redirect
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    return redirect('/ok')

@app.route('/ok')
def ok():
    return render_template('ok.html')