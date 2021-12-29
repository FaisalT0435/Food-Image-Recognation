from flask import Flask
from flask import render_template, request ,redirect, url_for
import requests
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ai'
mysql = MySQL(app)

url = "https://e27faf2cc66a42fbad2dce18747962e5.apig.cn-north-4.huaweicloudapis.com/v1/infers/a634ba73-1139-46b1-9c04-a1284586dbd1"
headers   = { "X-Apig-AppCode": "ddf28e37123a47a99ce6eda6645fc0e53aa68687dee4454aa716ce725e47552c" }


    
    
@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/recognize', methods = ['POST'])
def call_modelArts():
    f = request.files['imgFilename']
    print('recognize: '+f.filename)
    files = {"images": (f.filename, f.read(), f.content_type)}
    resp = requests.post(url, headers=headers, files=files)
    print('Result: '+resp.text)
    jsonResult = resp.json()
    result = jsonResult['predicted_label']
    arScores = jsonResult['scores']
    predicted_score = 0
    for score in arScores:
        if score[0]==result:
            predicted_score = float(score[1])
    print("Result: %s : predicted: %.2f" % (result, predicted_score))

    if resp.status_code == 200:     
        strStatus = "Success"
    else:
        strStatus = "Failed"
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO ai (File,Nama,Scores,Prediksi) Values(%s,%s,%s,%s)", (f.filename, result, predicted_score, strStatus)  )
    mysql.connection.commit()
    return render_template("result.html", food=result, status=strStatus, confidence=predicted_score)
    

@app.route('/hasil', methods = ['GET'])
def semua(): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ai")
    rv = cur.fetchall()
    cur.close()
    return render_template('hasil.html', computers=rv)
    
    
    

if __name__ == "__main__":
    app.run('127.0.0.1', port=8000, debug=True)
