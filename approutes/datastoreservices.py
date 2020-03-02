from flask import request, Blueprint, make_response
from google.cloud import datastore
from google.cloud import storage
import csv
import json
import base64
import datetime
import sys

# TODO implementare autorizzazione tramite token di autenticazione
# nel caso in cui non si dovesse usare il service account json

#creazione del blueprint da associare all'app principale
datastoreservices = Blueprint("datastoreservices", __name__)
#Inizializzazione dei client datastore e storage tramite il service account json
datastore_client = datastore.Client().from_service_account_json("config/key.json")
storage_client = storage.Client().from_service_account_json("config/key.json")
#Collegamento col bucket dedicato del progetto
bucket = storage_client.get_bucket("raspberrypersonal.appspot.com")

@datastoreservices.route("/putdatastore", methods=['POST'])
def put_data_to_datastore():
    #decodifica in base64 per poter leggere il messaggio come json
    payload = base64.b64decode(json.loads(request.data.decode('utf-8'))['message']['data'])
    #Estrazione del path dal json
    path = json.loads(payload)['path']
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


    # creiamo la response del servizio
    response = make_response(f"Aggiunti {len(put_list)} record al datastore")
    response.headers['Content-type'] = "text/plain"
    return response