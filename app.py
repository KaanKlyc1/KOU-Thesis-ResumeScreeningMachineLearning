
import glob
import os
import warnings
import requests
from flask import (Flask,session, g, json, Blueprint,flash, jsonify, redirect, render_template, request,
                   url_for, send_from_directory)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

import screen
import search


warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

app = Flask(__name__)

app.config.from_object(__name__) # load config from this file , flaskr.py
app.config.update(dict(
    SECRET_KEY='development key',
))

app.config['UPLOAD_FOLDER'] = 'Tr_Resumes/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

class jd:
    def __init__(self, name):
        self.name = name

def getfilepath(loc):
    temp = str(loc).split('\\')
    return temp[-1]
    

@app.route('/login', methods=['GET', 'POST'])
def login():
 error = None
 if request.method == 'POST':
    data = {
        'username': request.form['username'],
        'password': request.form['password'],
    }

    try:
        response = requests.post(
            'http://api-cbn.edu.ciloglunet.com/login',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data=data
        )

        responseData = json.loads(response.text)
        print(responseData)

        dataArray = list(responseData.values())
        print(dataArray[0])
        
        if dataArray[0] is True:
            session['logged_in'] = True
            
        else:
            raise Exception('Giriş bilgileri eksik ya da yanlış girdiniz')
    except Exception as error:
        _errorMessage = str(error)
        return render_template('login.html', error=_errorMessage)
    else:
        return redirect(url_for('home'))
    
 return render_template('login.html', error=error)



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


@app.route('/')
def home():
    x = []
    for file in glob.glob("./Job_Description/*.txt"):
        filepath = str(getfilepath(file))
        filename = filepath.replace(".txt","")
        x.append(jd(filename))
    print(x)
    return render_template('index.html', results = x)




@app.route('/results', methods=['GET', 'POST'])
def res():
    if request.method == 'POST':
        job= request.form['des']
        jobfile = job+ ".txt"
        print(jobfile)
        flask_return = screen.res(jobfile)
        
        print(flask_return)
        return render_template('result.html', results = flask_return)



@app.route('/resultscreen' ,  methods = ['POST', 'GET'])
def resultscreen():
    if request.method == 'POST':
        jobfile = request.form.get('Name')
        print(jobfile)
        print("EN UYGUNLAR BULUNUYOR")
        flask_return = screen.res(jobfile)
        return render_template('result.html', results = flask_return)



@app.route('/resultsearch' ,methods = ['POST', 'GET'])
def resultsearch():
    if request.method == 'POST':
        search_st = request.form.get('Name')
        print(search_st)
    result = search.res(search_st)
    # return result
    return render_template('result.html', results = result)

@app.route('/createjob' ,methods = ['POST', 'GET'])
def createjob():
    if request.method == 'POST':
        job_name = request.form.get('jobName')
        job_desc = request.form.get('jobDesc')
        
        with open('Job_Description/'+job_name+'.txt', 'x',encoding='utf-8') as f:
         f.write(str(job_desc))
        print("İş Tanımlandı")

    x = []
    for file in glob.glob("./Job_Description/*.txt"):
        filepath = str(getfilepath(file))
        filename = filepath.replace(".txt","")
        x.append(jd(filename))
    return render_template('index.html', results = x)

@app.route('/uploadcv' ,methods = ['POST', 'GET'])
def uploadcv():
    if request.method == 'POST':
        file = request.files['cv']
        file.save(f'Tr_Resumes/{file.filename}')

    x = []
    for file in glob.glob("./Job_Description/*.txt"):
        filepath = str(getfilepath(file))
        filename = filepath.replace(".txt","")
        x.append(jd(filename))
    return render_template('index.html', results = x)



@app.route('/Tr_Resumes/<path:filename>')
def custom_static(filename):
    return send_from_directory('./Tr_Resumes', filename)



if __name__ == '__main__':
    app.run('0.0.0.0' , 5000 , debug=True , threaded=True)
    
