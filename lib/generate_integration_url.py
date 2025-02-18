from string import Template
from helpers import query
from escape_helpers import sparql_escape_uri
from signinghub_api_client.client import SigningHubSession
from . import exceptions, query_result_helpers, signing_flow
from ..config import APPLICATION_GRAPH, SIGNINGHUB_IFRAME_REDIRECT_URL

# TODO: validation:
# - piece is uploaded to signinghub
def generate_integration_url(signinghub_session: SigningHubSession,
                             signflow_uri: str,
                             piece_uri: str,
                             collapse_panels: bool):
    pieces = signing_flow.get_pieces(signflow_uri)
    piece = query_result_helpers.ensure_1(pieces)
    if piece["uri"] != piece_uri:
        raise exceptions.InvalidStateException(f"Piece <{piece_uri}> is not linked to signflow <{signflow_uri}>.")

    query_string = _query_signinghub_document.substitute(
        graph=sparql_escape_uri(APPLICATION_GRAPH),
        signflow=sparql_escape_uri(signflow_uri),
        piece=sparql_escape_uri(piece_uri)
    )

    signinghub_document_result = query(query_string)
    signinghub_documents = query_result_helpers.to_recs(signinghub_document_result)
    signinghub_document = signinghub_documents[0]
    signinghub_package_id = signinghub_document["signinghub_package_id"]

    integration_url = signinghub_session.get_integration_link(signinghub_package_id, {
        "language":"nl-NL",
        # "user_email": "joe@gmail.com", # Know through SSO login?
        "callback_url": SIGNINGHUB_IFRAME_REDIRECT_URL,
        "collapse_panels": "true" if collapse_panels else "false",
        # "usercertificate_id": "31585" # Undocumented
    })

    return integration_url

_query_signinghub_document = Template("""
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
PREFIX sign: <http://mu.semte.ch/vocabularies/ext/handtekenen/>
PREFIX sh: <http://mu.semte.ch/vocabularies/ext/signinghub/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>

SELECT ?signinghub_document ?signinghub_package_id ?signinghub_document_id
WHERE {
    VALUES ?signflow { $signflow }
    VALUES ?piece { $piece }

    GRAPH $graph {
        ?signflow a sign:Handtekenaangelegenheid ;
            sign:doorlooptHandtekening ?sign_subcase .
        ?sign_subcase a sign:HandtekenProcedurestap .
        ?preparation_activity sign:voorbereidingVindtPlaatsTijdens ?sign_subcase .
        ?preparation_activity a sign:Voorbereidingsactiviteit ;
            sign:voorbereidingGenereert ?signinghub_document .
        ?signinghub_document a sh:Document ;
            sh:packageId ?signinghub_package_id ;
            sh:documentId ?signinghub_document_id ;
            prov:hadPrimarySource ?piece .
    }
}
""")