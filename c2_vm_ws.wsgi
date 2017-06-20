import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

def application(environ, start_response):
    # explicitly set environment variables from the WSGI-supplied ones
    ENVIRONMENT_VARIABLES = [
        'MAILSERVER_WS_TOKEN'
    ]
    for key in ENVIRONMENT_VARIABLES:
        if environ.get(key):
            os.environ[key] = environ.get(key)

    from mailserver_user_mgmt_ws import application as my_app

    return my_app(environ, start_response)
