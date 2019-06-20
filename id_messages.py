from pymongo import MongoClient

# Nos conectamos a la bdd
client = MongoClient('localhost')
db = client["g34"]
mensajes = db.mensajes

# función para setear id de mensajes
def set_ids():
    messages__id = list(mensajes.find({},{"_id":1}))
    id_count = 0;
    for m_id in messages__id:
        id = m_id["_id"]
        mensajes.update(
        { "_id": id },
        { "$set": { "id": id_count } }
        )
        id_count += 1

if __name__ == "__main__":
    set_ids()
