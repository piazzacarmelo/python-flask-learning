from flask import Flask,make_response, Blueprint
from google.cloud import datastore
from google.cloud import storage
from google.cloud import pubsub
import json
import csv
import datetime


#creazione del blueprint da associare all'app principale
subscriber = Blueprint("subscriber", __name__)
#Inizializzazione dei client datastore e storage tramite il service account json
datastore_client = datastore.Client().from_service_account_json("config/key.json")
storage_client = storage.Client().from_service_account_json("config/key.json")
#Collegamento col bucket dedicato del progetto
bucket = storage_client.get_bucket("raspberrypersonal.appspot.com")

# Callback function da utilizzare al momento della ricezione del messaggio
# TODO gestire caso di errore
def put_data_datastore(message):
    #decodifica dei bytes per ottenere il path dall'oggetto JSON
    print(message.data)
    path = json.loads(bytes.decode(message.data,encoding='utf-8'))['path']
    print(path)
    #get del blob dal path precedente -> list di linee
    blob = bucket.get_blob(path).download_as_string().decode('utf-8').splitlines()
    #lettura della lista come csv
    csv_reader = csv.reader(blob, delimiter=';')
    #inizializzazione della lista delle upsert
    put_list = []
    #loop per mappare le colonne del csv nell'entity
    for row in csv_reader:
        #chiave da utilizzare per l'upsert compreso di namespace
        complete_key = datastore_client.key("Articolo", row[0], namespace="Anagrafiche")
        entity = datastore.Entity(key=complete_key, exclude_from_indexes=['dt_mod'])
        entity.update({
            "artcod": row[0],
            "dxe": row[1],
            "merceolcod": row[2],
            "dt_mod" : datetime.datetime.now().strftime(("%Y%m%d%H%M%S"))
        })
        #aggiunta dell'entity nella lista
        put_list.append(entity)

    # upsert in bulk dei record
    datastore_client.put_multi(put_list)
    #acknowledge del messaggio
    message.ack()
    return (f"Aggiunti {len(put_list)} record al datastore")
    
def start_streaming():
    #inizializzazione del subscriber client tramite il service account json
    subscriber = pubsub.SubscriberClient().from_service_account_json("config/key.json")

    #Variabili necessarie alla creazione del subscriber
    project_id = "raspberrypersonal"
    subscribtion = "PullSub"

    #creaimo l'oggetto subscribe
    subscription_name = f'projects/{project_id}/subscriptions/{subscribtion}'

    #Avvio dello streaming in polling sulla coda
    consumer = subscriber.subscribe(subscription_name, put_data_datastore)

    #Start pull streaming
    try:
        print("Start subscriber")
        consumer.result()
    except KeyboardInterrupt:
        consumer.cancel()

    return("Done")


#Servizio per startare il subscriber
@subscriber.route("/startsubstream", methods=['GET'])
def start():
    response = make_response(f"Starting Streaming".join(start_streaming()))
    response.headers['Content-type'] = "text/plain"
    return response