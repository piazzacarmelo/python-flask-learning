from flask import Flask, make_response
from approutes.repo_get_test import repo_get_test
from approutes.datastoreservices import datastoreservices
from approutes.subscriber import subscriber
import json

#Nome dell'app
app = Flask(__name__)
#Abilitazione del prettify json
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
#Registrazione dei vari blueprint
app.register_blueprint(repo_get_test)
app.register_blueprint(datastoreservices)
app.register_blueprint(subscriber)

#approute sull'url iniziale che mostra una lista dei servizi presenti
# TODO renderizzare una pagina web tramite flask per un feedback visivo migliore
@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def home():
    # TODO auto create json based on operations allowed
    response = make_response(json.dumps({"Lista endpoint": [{"uri" : "/getrepo","method" : "POST","parametri_input" :
        "Header -> token","description" : "Servizio che richiama le api di GitHub per restituire un json con le "
        "informazioni dei repository"},{"uri" : "/getrepo","method" : "GET","parametri_input" : "param -> token",
        "description" : "Servizio che richiama le api di GitHub per restituire un json con le informazioni dei"
        " repository"},{"uri" : "/putdatastore","method" : "POST","parametri_input" : "data -> topic message",
        "description" : "Servizio che riceve in input un messaggio da un topic contenente il path di un file da"
        " importare nel datastore"}]},sort_keys = True, indent = 4))
    response.headers['Content-type'] = "application/json"
    return response

#Valido per i test in locale
if __name__ == "__main__":
    app.run()