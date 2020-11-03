import os
from functools import wraps
from flask import g, request
from pytz import timezone
from signinghub_api_client.client import SigningHubSession
from signinghub_api_client.exceptions import SigningHubException
from helpers import log, error
from .queries.session import construct_get_mu_session_query, \
    construct_get_signinghub_session_query, construct_insert_signinghub_session_query
from .sudo_query import sudo_query, sudo_update

TIMEZONE = timezone('Europe/Brussels')

SIGNINGHUB_API_URL = os.environ.get("SIGNINGHUB_API_URL", "test")
CERT_FILE_PATH = os.environ.get("CERT_FILE_PATH", "/certs/certificate.crt")
KEY_FILE_PATH = os.environ.get("KEY_FILE_PATH", "/certs/private_key.pem")

SIGNINGHUB_SSO_METHOD = "test"

def open_new_signinghub_session(oauth_token, mu_session_uri):
    sh_session = SigningHubSession(SIGNINGHUB_API_URL)
    sh_session.cert = (CERT_FILE_PATH, KEY_FILE_PATH) # For authenticating against VO-network
    sh_session.authenticate_sso(oauth_token, SIGNINGHUB_SSO_METHOD)
    sh_session_params = {
        "creation_time": sh_session.last_successful_auth_time,
        "expiry_time": sh_session.last_successful_auth_time + sh_session.access_token_expiry_time,
        "token": sh_session.access_token
    }
    sh_session_query = construct_insert_signinghub_session_query(sh_session_params, mu_session_uri)
    sudo_update(sh_session_query)
    return sh_session

def ensure_signinghub_session(mu_session_uri):
    mu_session_query = construct_get_mu_session_query(mu_session_uri)
    mu_session_result = sudo_query(mu_session_query)['results']['bindings']
    if not mu_session_result:
        return error("Didn't find a mu-session with an Oauth token.")
    mu_session = mu_session_result[0]
    sh_session_query = construct_get_signinghub_session_query(mu_session_uri)
    sh_session_results = sudo_query(sh_session_query)['results']['bindings']
    if sh_session_results: # Restore SigningHub session
        log("Found a valid SigningHub session.")
        sh_session_result = sh_session_results[0]
        g.sh_session = SigningHubSession(SIGNINGHUB_API_URL)
        g.sh_session.cert = (CERT_FILE_PATH, KEY_FILE_PATH) # For authenticating against VO-network
        g.sh_session.access_token = sh_session_result["token"]
    else: # Open new SigningHub session
        log("No valid SigningHub session found. Opening a new one ...")
        try:
            g.sh_session = open_new_signinghub_session(mu_session["oauthToken"], mu_session_uri)
        except SigningHubException:
            return error("Didn't manage to authenticate at SigningHub.")


def signinghub_session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        mu_session_id = request.headers["MU-SESSION-ID"]
        error_response = ensure_signinghub_session(mu_session_id)
        if error_response:
            return error_response
        return f(*args, **kwargs)
    return decorated_function
