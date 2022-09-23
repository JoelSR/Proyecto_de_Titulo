#from flask.globals import session
#from sqlalchemy import schema
#from .entities.entity import Session, engine, Base
#from .entities.exam import Exam, ExamSchema
from dis import dis
import mimetypes
from flask import Flask, jsonify, request, flash, send_file
from flask.wrappers import Response
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import base64
import scipy.io as sio
import shutil
import sys
import os
from io import BytesIO
#sys.path.insert(1, 'Reidmen Fenics/ipnyb propagation')
from dotenv import load_dotenv

load_dotenv()

#Local reference
#sys.path.append("Reidmen Fenics/ipnyb propagation")

#Docker reference
sys.path.append("src/Reidmen Fenics/ipnyb propagation")

print(sys.path)
Reidmen = __import__("TimeSimTransIsoMatCij2D_test")

# creating the Flask application
app = Flask(__name__)

# New begin

# app.use()




app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PORT'] =  int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB') # proyecto-v01 para win y proyecto_v01 para linux
app.config['CORS_HEADERS'] = os.getenv('CORS_HEADERS')


# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# #app.config['MYSQL_PORT'] =  os.getenv('MYSQL_PORT')
# #app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
# app.config['MYSQL_DB'] = 'proyecto_v01' # proyecto-v01 para win y proyecto_v01 para linux
# app.config['CORS_HEADERS'] = 'Content-Type'

mysql = MySQL(app)

CORS(app)
#, resouces={r"/*": {"origins": "*"}}, supports_credentials = True
#cors = CORS(app, resources={r"/*": {"origins": "*"}})


# settings
app.secret_key = "110997"


@app.route('/')
def Index():
    return '<h1>Hello world<h1>'


@app.route('/Test')
def test():

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM timesimtransisomat_first_step01')
    data = cur.fetchall()
    cur.close()
    print('valor de data:', data)
    for item in data:
        print(item)


    return jsonify(results=data)
    #return json.dumps({'favorite_colors': favorite_colors()})



@app.route('/Input_data', methods=['POST'])
def input_data():
    #print(request.json['status'])
    #print(request)
    n_transmitter = request.json['n_transmitter'],
    n_receiver = request.json['n_receiver'],
    distance = request.json['distance'],
    plate_thickness = request.json['plate_thickness'],
    porosity = request.json['porosity']
    status = request.json['status']
    print("Distance", distance)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO timesimtransisomat_first_step01 (n_transmitter, n_receiver, distance, plate_thickness, porosity, p_status) VALUES (%s,%s,%s,%s,%s,%s)",
                (n_transmitter, n_receiver, distance, plate_thickness, porosity, status))
    print(cur.lastrowid)
    last_id = cur.lastrowid
    mysql.connection.commit()
    flash('data Added successfully')
    return 'ok'


@app.route('/Load_data', methods=['GET'])
def load_data():
    data_t = []
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM timesimtransisomat_first_step01')
    data = cur.fetchall()
    cur.close()
    for doc in data:
        data_t.append({
            'id': doc[0],
            'n_transmitter': doc[1],
            'n_receiver': doc[2],
            'distance': doc[3],
            'plate_thickness': doc[4],
            'porosity': float(doc[5]),
            'p_status' : doc[7]
        })
    return jsonify(data_t)


@app.route('/Load_data/<id>', methods=['GET'])
def load_data_id(id):
    data_t = []
    sub_id = id
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM timesimtransisomat_first_step01 WHERE id = {0}".format(sub_id))
    data = cur.fetchall()
    cur.close()
    for doc in data:
        data_t.append({
            'id': doc[0],
            'n_transmitter': doc[1],
            'n_receiver': doc[2],
            'distance': doc[3],
            'plate_thickness': doc[4],
            'porosity': float(doc[5]),
            'p_status' : doc[7],
            'time' : str(doc[8])
        })
    return jsonify(data_t)

@app.route('/Load_data/porosity/<v>', methods=['GET'])
def load_data_porosity(v):
    #print(request)
    data_t = []
    poro = v
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM timesimtransisomat_first_step01 WHERE porosity = {0}".format(poro))
    data = cur.fetchall()
    print(data)
    cur.close()
    for doc in data:
        data_t.append({
            'id': doc[0],
            'n_transmitter': doc[1],
            'n_receiver': doc[2],
            'distance': doc[3],
            'plate_thickness': doc[4],
            'porosity': float(doc[5]),
            'p_status' : doc[7]
        })
    return jsonify(data_t)
    #print (data)

@app.route('/Load_data/distance/<v>', methods=['GET'])
def load_data_distance(v):
    #print(request)
    data_t = []
    distance = v
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM timesimtransisomat_first_step01 WHERE distance = {0}".format(distance))
    data = cur.fetchall()
    cur.close()
    for doc in data:
        data_t.append({
            'id': doc[0],
            'n_transmitter': doc[1],
            'n_receiver': doc[2],
            'distance': doc[3],
            'plate_thickness': doc[4],
            'porosity': float(doc[5]),
            'p_status' : doc[7]
        })
    return jsonify(data_t)
    #print (data)

@app.route('/Load_data/download/<v>', methods=['GET'])
def load_data_download(v):
    #print(request)
    cur = mysql.connection.cursor()
    cur.execute("select image, result_step_01 from timesimtransisomat_first_step01 WHERE id = {0}".format(v))
    data = cur.fetchone()
    filedata = data[0]
    filename = data[1]

    # Decode the string
    binary_data = base64.b64decode(filedata)
	
    return send_file(BytesIO(binary_data), as_attachment = True, download_name = filename, mimetype='mat')


@app.route('/load_data_PUT/<id>', methods=['PUT'])
def load_result_id_put(id):
    sub_id = id
    
    n_transmitter = request.json['n_transmitter']
    n_receiver = request.json['n_receiver']
    distance = request.json['distance']
    plate_thickness = request.json['plate_thickness']
    porosity = request.json['porosity']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE timesimtransisomat_first_step01 SET p_status = 'In progress'  WHERE id = {0};".format(sub_id))
    mysql.connection.commit()
   
  
    filename,time = Reidmen.fmain(n_transmitter,n_receiver,distance,plate_thickness,porosity,sub_id)
    print("Nombre archivo",filename)

    filepath = "src/Reidmen Fenics/ipnyb propagation/Files_mat/" + filename
    
    file = read_file(filepath)

    cur = mysql.connection.cursor()
    sql = "UPDATE timesimtransisomat_first_step01 SET result_step_01 = %s, p_status = 'Done', time = %s, image = %s  WHERE id = %s;"
    cur.execute(sql,(filename, time, file, sub_id))
    mysql.connection.commit()

    if os.path.exists(filepath):
        os.remove(filepath)
        print("Archivo temporal removido.")
    else:
        print("No se encuentra el archivo indicado a eliminar.")
        
    return('Ok')
    
   
@app.route('/Load_data_test/<id>', methods=['GET'])
def load_data_id_test(id):
    data_t = []
    sub_id = id
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM timesimtransisomat_first_step01 WHERE id = {0}".format(sub_id))
    data = cur.fetchall()
    cur.close()
    for doc in data:
        data_t.append({
            'id': doc[0],
            'n_transmitter': doc[1],
            'n_receiver': doc[2],
            'distance': doc[3],
            'plate_thickness': doc[4],
            'porosity': float(doc[5]),
            'result_step_01': doc[6],
            'p_status' : doc[7],
            'time' : str(doc[8])
        })
    return jsonify(data_t)
    
    
    #cur.execute("UPDATE timesimtransisomat_first_step01 SET porosity = {0}, n_transmitter = {1}, n_receiver = {2}, distance = {3}, plate_thickness = {4}  WHERE id = {5};".format(
    #     plus, n_transmitter, n_receiver, distance, plate_thickness, sub_id))
    
    return 'Funciona'



def read_file(filename):
    with open(filename, 'rb') as f:
        matfile = f.read()
    return matfile


@app.route('/Result')
def result():
    return 'result'

if __name__ == '__main__':
    app.run(port=3000, debug=False, host='0.0.0.0')
