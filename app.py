from flask import Flask, render_template, request, abort, json
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os
import atexit
import subprocess

USER_KEYS = ['name', 'last_name', 'occupation', 'follows', 'age']
MESS_KEYS = ['message', 'lat', 'long', 'date']

# Levantamos el servidor de mongo. Esto no es necesario, puede abrir
# una terminal y correr mongod. El DEVNULL hace que no vemos el output
#mongod = subprocess.Popen('mongod', stdout=subprocess.DEVNULL)
# Nos aseguramos que cuando el programa termine, mongod no quede corriendo
#atexit.register(mongod.kill)

# El cliente se levanta en localhost:5432
uri = "mongodb://grupo19:grupo19@146.155.13.149/grupo19?authSource=admin"
client = MongoClient(uri)
# Utilizamos la base de datos 'entidades'
db = client.get_database()
# Seleccionamos la colección de usuarios y mensajes
usuarios = db.usuarios
mensajes = db.mensajes

# Iniciamos la aplicación de flask
app = Flask(__name__)

######################### RUTAS GET ENUNCIADO #################################

# Enunciado: i
@app.route("/messages/<int:mid>")
def get_message(mid):
    messages = list(mensajes.find({"id": mid}, {}))
    return json.jsonify(messages)


# Enunciado: ii
@app.route("/usermessages/<int:uid>")
def get_usermessages(uid):
    messages = list(mensajes.find({"sender": uid}, {"_id": 0, "message": 1, "sender": 1}))
    return json.jsonify(messages)

# Enunciado: iii
def date_func(arr):
    return arr["date"]

@app.route("/conversation/<int:uid1>/<int:uid2>")
def get_conversation(uid1, uid2):
    messages = list(mensajes.find(
    {"$or": [{"$and": [{"sender": uid2}, {"receptant": uid1}]},
            {"$and": [{"sender": uid1}, {"receptant": uid2}]}]},
    {"_id": 0}))
    messages.sort(key=date_func)
    return json.jsonify(messages)


#################### RUTAS TEXT SEARCH ENUNCIADO ###############################

# /messages/?siosi=frase1,frase2&pueden=palabra1,palabra2&no=palabra1,palabra2
def get_search():
    si_o_si = request.args.get('siosi')
    pueden = request.args.get('pueden')
    no = request.args.get('no')

    if si_o_si is not None: si_o_si = si_o_si.split(',')
    if pueden is not None: pueden = pueden.split(',')
    if no is not None: no = no.split(',')

    final_search = ""
    if si_o_si is not None and len(si_o_si) != 0:
        final_search += "\"{}\"".format("\" \"".join(si_o_si))

    if pueden is not None and len(pueden) != 0:
        final_search += " {}".format(" ".join(pueden))

    if no is not None and len(no) != 0:
        final_search += " -{}".format(" -".join(no))

    return final_search

# Enunciado: iv message
@app.route("/messages")
def get_mensajeidentico():
    final_search = get_search()
    # print(final_search)
    if final_search == "": mensajes_iden = list(mensajes.find({}, { "message": 1, "_id": 0 }))
    else: mensajes_iden = list(mensajes.find({ '$text': { '$search': final_search } }, { "message": 1, "_id": 0 } ))
    # print(len(mensajes_iden))
    return json.jsonify(mensajes_iden)



################## RUTAS POST/DELETE ENUNCIADO  ###############################

# Enunciado: vii

@app.route("/newconversation/<int:uid1>/<int:uid2>", methods=['POST'])
def create_conversation(uid1, uid2):
    # Se genera el mid
    data = {key: request.json[key] for key in MESS_KEYS}
    count = mensajes.count_documents({})
    data["sender"] = uid1
    data["receptant"] = uid2
    data["id"] = count + 1


    # Insertar retorna un objeto
    result = mensajes.insert_one(data)

    # Creo el mensaje resultado
    if (result):
        message = "1 mensaje insertado desde el usuario:{} al usuario: {}".format(uid1, uid2)
        success = True
    else:
        message = "No se pudo insertar el mensaje"
        success = False


    # Retorno el texto plano de un json
    return json.jsonify({'success': success, 'message': message})


# Enunciado: viii

@app.route('/delmessages/<int:mid>', methods=['DELETE'])
def delete_message(mid):

    # esto borra el primer resultado. si hay mas, no los borra
    mensajes.delete_one({"id": mid})

    message = f'El mensaje con id={mid} ha sido eliminado.'

    # Retorno el texto plano de un json
    return json.jsonify({'result': 'success', 'message': message})


####

@app.route("/")
def home():
    return "<h1>HELLO</h1>"

# Mapeamos esta función a la ruta '/plot' con el método get.
@app.route("/plot")
def plot():
    # Obtengo todos los usuarios
    users = usuarios.find({}, {"_id": 0})

    # Hago un data frame (tabla poderosa) con la columna 'name' indexada
    df = pd.DataFrame(list(users)).set_index('name')

    # Hago un grafico de pi en base a la edad
    df.plot.pie(y='age')

    # Export la figura para usarla en el html
    pth = os.path.join('static', 'plot.png')
    plt.savefig(pth)

    # Retorna un html "rendereado"
    return render_template('plot.html')


@app.route("/users")
def get_users():
    resultados = [u for u in usuarios.find({}, {"_id": 0})]
    # Omitir el _id porque no es json serializable

    return json.jsonify(resultados)


@app.route("/users/<int:uid>")
def get_user(uid):
    users = list(usuarios.find({"uid": uid}, {"_id": 0}))

    return json.jsonify(users)


@app.route("/users", methods=['POST'])
def create_user():
    '''
    Crea un nuevo usuario en la base de datos
    Se  necesitan todos los atributos de model, a excepcion de _id
    '''

    # Si los parámetros son enviados con una request de tipo application/json:
    data = {key: request.json[key] for key in USER_KEYS}

    # Se genera el uid
    count = usuarios.count_documents({})
    data["uid"] = count + 1

    # Insertar retorna un objeto
    result = usuarios.insert_one(data)

    # Creo el mensaje resultado
    if (result):
        message = "1 usuario creado"
        success = True
    else:
        message = "No se pudo crear el usuario"
        success = False

    # Retorno el texto plano de un json
    return json.jsonify({'success': success, 'message': message})


@app.route('/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    '''
    Elimina un usuario de la db.
    Se requiere llave uid
    '''

    # esto borra el primer resultado. si hay mas, no los borra
    usuarios.delete_one({"uid": uid})

    message = f'Usuario con id={uid} ha sido eliminado.'

    # Retorno el texto plano de un json
    return json.jsonify({'result': 'success', 'message': message})


@app.route('/users/many', methods=['DELETE'])
def delete_many_user():
    '''
    Elimina un varios usuarios de la db.
    - Se requiere llave idBulk en el body de la request application/json
    '''

    if not request.json:
        # Solicitud faltan parametros. Codigo 400: Bad request
        abort(400)  # Arrojar error

    all_uids = request.json['uidBulk']

    if not all_uids:
        # Solicitud faltan parametros. Codigo 400: Bad request
        abort(400)  # Arrojar error

    # Esto borra todos los usuarios con el id dentro de la lista
    result = usuarios.delete_many({"uid": {"$in": all_uids}})

    # Creo el mensaje resultado
    message = f'{result.deleted_count} usuarios eliminados.'

    # Retorno el texto plano de un json
    return json.jsonify({'result': 'success', 'message': message})


@app.route("/test")
def test():
    # Obtener un parámero de la URL
    param = request.args.get('name', False)
    print("URL param:", param)

    # Obtener un header
    param2 = request.headers.get('name', False)
    print("Header:", param2)

    # Obtener el body
    body = request.data
    print("Body:", body)

    return "OK"


if os.name == 'nt':
    app.run()
