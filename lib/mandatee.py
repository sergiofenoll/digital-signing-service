from helpers import query, log
from typing import Callable
from ..queries.mandatee import construct_get_mandatee, \
    construct_get_mandatee_by_id, construct_get_active_mandatee_by_email
from .exceptions import NoQueryResultsException
from ..config import APPLICATION_GRAPH

def get_mandatee_by_id(mandatee_id):
    query_str = construct_get_mandatee_by_id(mandatee_id)
    mandatee_results = query(query_str)['results']['bindings']
    if not mandatee_results:
        raise NoQueryResultsException("No mandatee found by id '{}'".format(mandatee_id))
    return mandatee_results[0]["uri"]["value"]

def get_mandatee(mandatee_uri, query_method: Callable = query):
    query_str = construct_get_mandatee(mandatee_uri)
    madatee_results = query_method(query_str)['results']['bindings']
    if not madatee_results:
        raise NoQueryResultsException("No mandatee with configured user account found by uri <{}>".format(mandatee_uri))
    mandatee = {k: v["value"] for k, v in madatee_results[0].items()}
    return mandatee

def get_active_mandatee_by_email(mandatee_email, query_method: Callable = query):
    query_str = construct_get_active_mandatee_by_email(mandatee_email)
    madatee_results = query_method(query_str)['results']['bindings']
    if not madatee_results:
        raise NoQueryResultsException("No mandatee with configured user account found by e-mail address '{}'".format(mandatee_email))
    if madatee_results.length > 1:
        log("Multiple mandatees found for e-mail address '{}'. Picking one.".format(mandatee_email))
    mandatee = {k: v["value"] for k, v in madatee_results[0].items()}
    return mandatee
