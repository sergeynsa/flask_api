from functools import wraps
from flask import request, Response
from flask import render_template

from flask import abort, request
from flask import Flask
import json
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

#An open list of IP addresses
with open("ipsList.txt", "r") as f:
    ip_list=[ip.strip() for ip in f.readlines()]

print(ip_list)

@app.before_request
def limit_remote_addr():
     if request.remote_addr in ip_list:
        abort(500)  # 403 is suitable too, also I will use filtration by other parts of my system

def check_auth(username, password):
    app.logger.info(f'Checking auth for user {username}')
    # Of course this authentication machinery is very primitive and just for illustration"
    return username == 'admin' and password == '***'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/enroll', methods=['GET'])
@requires_auth
def enroll():
    all_args = request.args

    if 'age' not in all_args or 'name' not in all_args or 'address' not in all_args:
        return Response('Not enough GET keys. Should be age, name and address', 401)

    if not all_args['age'].isdigit():
        return Response('Age is not int', 401)
    elif all_args['name'].isdigit():
        return Response('Name consists just from digits', 401)
    elif all_args['address'].isdigit():
        return Response('Address consists just from digits', 401)

    return Response('Hello!', 200)


@app.route('/resign', methods=['POST'])
@requires_auth
def resign():
    post_body = request.data
    try:
        json.loads(post_body)
    except json.JSONDecodeError as ex:
        return Response(f'Json parsing error: {ex}', 400)
    return Response('Json is valid', 200)


# Pay attention that serving this app with default flask development server intended for single client usage
if __name__ == '__main__':
    handler = RotatingFileHandler('auth.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
