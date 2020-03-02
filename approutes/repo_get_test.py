from flask import request, Blueprint,make_response
from helper.utility import prettify_json
import requests

#Blueprint di test locale

repo_get_test = Blueprint("repo_get_test", __name__)

@repo_get_test.route("/getrepo", methods=["POST"])
def getRepoPOST():
    token = request.headers.get("token")
    headers = {"Authorization": f"token {token}"}
    return prettify_json(requests.get("https://api.github.com/user/repos", headers=headers).json())

@repo_get_test.route("/getrepo", methods=["GET"])
def getRepoGET():
    token = request.args.get("token")
    headers = {"Authorization": f"token {token}"}
    if (request.args.get("onlynames")):
        # TODO performance tests
        # 1st: make a list then map to a string
        response = requests.get("https://api.github.com/user/repos", headers=headers).json()
        list = []
        for element in response:
            list.append(element['name'] + "\n")
        response = make_response(''.join(map(str,list)))
        response.headers['Content-type'] = "text/plain"
        return response
        # 2nd: make an empty string and keep joining the elements
        #response = requests.get("https://api.github.com/user/repos", headers=headers).json()
        #listStrings = ''
        #for element in response:
        #    listStrings.join(element['name'] + "\n")
        #response = make_response(listStrings)
        #response.headers['Content-type'] = "text/plain"
        #return response
    else:
        response = requests.get("https://api.github.com/user/repos", headers=headers).json()
        return prettify_json(response)