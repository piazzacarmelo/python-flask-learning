from flask import make_response
import json

### Auto prettify and response generator
def prettify_json(arg):
    response = make_response(json.dumps(arg, sort_keys = True, indent = 4))
    response.headers['Content-type'] = "application/json"
    return response