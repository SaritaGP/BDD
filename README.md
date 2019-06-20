# gunicorn-flask-pipenv-sample

## Para correr

### Windows con una sola version de python, Ubuntu 18.04+

```bash
pip install pipenv
```

### Otros

```bash
pip3 install pipenv
```

Abrimos nuevamente la consola

#### Crear entorno

```bash
pipenv install
```

### Preparar MongoDB
Se debe tener instalado MongoDB. Instalador disponeible  con instrucciones en
https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/

Se debe configurar variable de entorno para mongod.exe y mongo.exe
La ruta default es: C:\Program Files\MongoDB\Server\4.0\bin

Con instalación default de MongoDB, asegurar que existan directorios C:\data\db

Ejecutar mongod
```bash
cd <directorio proyecto>
mongod
```
Debería quedar servidor abierto en esa prompt

Abrir otra cmd en directorio de proyecto e importar los datos
```bash
cd <directorio proyecto>
mongoimport --db g34 --collection mensajes --drop --file data/messages.json --jsonArray
mongoimport -d g34 -c usuarios --type csv --file data/usuario.csv --headerline
```
Nos aseguramos de que se hayan importado correctamente:
```bash
mongo
> use g34
> show collections;
```
//debería imprimir 'mensajes'

Ahora para setear los id a mensajes salimos de la shell de mongo y entramos
a pipenv
```bash
> exit
pipenv shell
()> python id_messages.py
```
Se puede verificar que los mensajes ahora tienen el parametro "id"
```bash
mongo
> use g34
> db.mensajes.find({},{"id":1})
```

### Correr
```bash
pipenv shell
```
Si estas en windows
```
python main.py
```

Cualquier otro sistema operativo
```
gunicorn main:app --workers=3 --reload
```

### Rutas Enunciado
"Una ruta que al recibir el id de un mensaje, obtenga toda la información
asociada a ese mensaje" : "/messages/<int:mid>"
Para esta ruta se le agrego un id a los mensajes que son enteros partiendo desde el 0

"Una ruta que al recibir el id de un usuario, obtenga toda la información de ese usuario, junto con los mensajes emitidos por él.
": "/usermessages/<int:uid>"

"Una ruta que al recibir el id de dos usuarios, obtenga todos los mensajes intercambiados entre dichos usuarios.
": "/conversation/<int:uid1>/<int:uid2>"

"Obtener mensajes mediante búsqueda por texto": /messages/?siosi=frase1,frase2&pueden=palabra1,palabra2&no=palabra1,palabra2
siosi es para la búsqueda de una o más frases que deben estar en el mensaje, si son más de 1 frase estas se deben separar por COMA (,)
pueden es para la búsqueda de una o más palabras que pueden o no estar en el mensaje, si es más de una palabra se deben separar por COMA (,)
no es para la búsqueda de una o más que no pueden estar en el mensaje, si es más de una palabra se deben separar por COMA (,)

"Dado dos ids de usuarios i y j, una ruta que inserte un mensaje a la base de datos que esta ́ enviando el usuario i al usuario j."
: "/newconversation/<int:uid1>/<int:uid2>"

"Dado un id de mensaje, se debe eliminar ese mensaje." : "/delmessages/<int:mid>"

### Supuestos
Para la ruta del método POST, asumimos que en el body se entregará el dato "lat", "lon" y "date".
Para la búsqueda de palabras que NO deben estar en el mensaje se asume que en primer lugar debe existir al menos una palabra o frase que puede o debe estar en el mensaje.
