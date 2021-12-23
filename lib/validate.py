from string import Template
from helpers import query
from escape_helpers import sparql_escape_uri, sparql_escape_string
from . import helpers, exceptions, get_signflow_pieces
from ..config import KANSELARIJ_GRAPH

def ensure_signflow_exists(signflow_uri):
    if not signflow_exists(signflow_uri):
        raise exceptions.ResourceNotFoundException(signflow_uri)

def signflow_exists(signflow_uri):
    exists_template = Template("""
        PREFIX sign: <http://mu.semte.ch/vocabularies/ext/handteken/>
        
        ASK {
            $signflow a sign:Handtekenaangelegenheid .
        }
    """)
    
    existence_test_query_string = exists_template.substitute(
        graph=sparql_escape_uri(KANSELARIJ_GRAPH), # TODO: determine why this cannot be the application graph
        signflow=sparql_escape_uri(signflow_uri),
    )

    result = query(existence_test_query_string)
    exists = helpers.to_answer(result)
    return exists

def ensure_piece_exists(piece_uri):
    if not piece_exists(piece_uri):
        raise exceptions.ResourceNotFoundException(piece_uri)

def piece_exists(piece_uri):
    exists_template = Template("""
        PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
        
        ASK {
            $piece a dossier:Stuk .
        }
    """)
    
    existence_test_query_string = exists_template.substitute(
        graph=sparql_escape_uri(KANSELARIJ_GRAPH), # TODO: determine why this cannot be the application graph
        piece=sparql_escape_uri(piece_uri)
    )

    result = query(existence_test_query_string)
    exists = helpers.to_answer(result)
    return exists

def ensure_signer_exists(signer_uri):
    if not piece_exists(signer_uri):
        raise exceptions.ResourceNotFoundException(signer_uri)
