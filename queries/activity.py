import os
from string import Template
from datetime import datetime
from pytz import timezone
from escape_helpers import sparql_escape_uri, sparql_escape_string, sparql_escape_int, sparql_escape_datetime

TIMEZONE = timezone('Europe/Brussels')
APPLICATION_GRAPH = "http://mu.semte.ch/application"

SIGNING_PREP_ACT_TYPE_URI = "http://kanselarij.vo.data.gift/id/concept/activiteit-types/001d38fb-b285-41ef-a252-4e70208e9266"
SIGNING_ACT_TYPE_URI = "http://mu.semte.ch/vocabularies/ext/publicatie/Handtekenactiviteit"
SIGNING_WRAP_TYPE_URI = "http://kanselarij.vo.data.gift/id/concept/activiteit-types/d05978cb-3219-4ed4-9ab5-45b03c58a0ae"

SH_DOC_TYPE_URI = "http://mu.semte.ch/vocabularies/ext/signinghub/Document"

sh_package_base_uri = os.environ.get("SIGNINGHUB_API_URL", "http://kanselarij.vo.data.gift/").strip("/") + "/"
SH_DOC_BASE_URI = "{}package/{{package_id}}/document/{{document_id}}".format(sh_package_base_uri)

def construct_get_signing_prep_from_sh_package_id(sh_package_id,
                                                  graph=APPLICATION_GRAPH):
    query_template = Template("""
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX sh: <http://mu.semte.ch/vocabularies/ext/signinghub/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>

SELECT DISTINCT (?signing_prep AS ?uri) ?sh_document_id ?used_file
WHERE {
    GRAPH $graph {
        ?signing_prep a prov:Activity ;
            dct:type $prep_type .
        ?signing_prep sh:document ?sh_doc ;
            ext:gebruiktBestand ?used_file .
        ?sh_doc sh:packageId $sh_package_id ;
            sh:documentId ?sh_document_id .
    }
}
""")
    return query_template.substitute(
        graph=sparql_escape_uri(graph),
        prep_type=sparql_escape_uri(SIGNING_PREP_ACT_TYPE_URI),
        sh_package_id=sparql_escape_string(sh_package_id))

def construct_end_prep_start_signing(signing_prep_uri,
                                     time,
                                     graph=APPLICATION_GRAPH):
    query_template = Template("""
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>

INSERT {
    GRAPH $graph {
        $signing_prep dossier:Activiteit.einddatum $time .
        ?signing dossier:Activiteit.startdatum $time .
    }
}
WHERE {
    GRAPH $graph {
        $signing_prep a prov:Activity ;
            dct:type $prep_type .
        ?signing a prov:Activity ;
            dct:type $sig_type ;
            prov:wasInformedBy $signing_prep .
    }
}
""")
    return query_template.substitute(
        graph=sparql_escape_uri(graph),
        signing_prep=sparql_escape_uri(signing_prep_uri),
        prep_type=sparql_escape_uri(SIGNING_PREP_ACT_TYPE_URI),
        sig_type=sparql_escape_uri(SIGNING_ACT_TYPE_URI),
        time=sparql_escape_datetime(time))

def construct_update_signing_activity(sh_package_id,
                                      sh_document_id,
                                      mandatee_uri,
                                      end_time,
                                      graph=APPLICATION_GRAPH):
    query_template = Template("""
PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX sh: <http://mu.semte.ch/vocabularies/ext/signinghub/>
PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>

INSERT {
    GRAPH $graph {
        ?signing dossier:Activiteit.einddatum $end_time .
    }
}
WHERE {
    GRAPH $graph {
        ?signing_prep a prov:Activity ;
            dct:type $prep_type ;
            sh:document ?sh_doc .
        ?sh_doc sh:packageId $sh_package_id ;
            sh:documentId $sh_document_id .
        ?signing a prov:Activity ;
            dct:type $type ;
            prov:wasInformedBy ?signing_prep ;
            prov:qualifiedAssociation $mandatee .
        $mandatee a mandaat:Mandataris .
        FILTER NOT EXISTS { ?signing dossier:Activiteit.einddatum ?end_time . }
    }
}
""")
    return query_template.substitute(
        graph=sparql_escape_uri(graph),
        prep_type=sparql_escape_uri(SIGNING_PREP_ACT_TYPE_URI),
        sh_package_id=sparql_escape_string(sh_package_id),
        sh_document_id=sparql_escape_string(sh_document_id),
        sig_type=sparql_escape_uri(SIGNING_ACT_TYPE_URI),
        mandatee=sparql_escape_uri(mandatee_uri),
        end_time=sparql_escape_datetime(end_time))

def construct_insert_wrap_up_activity(sh_package_id,
                                      sh_document_id,
                                      signed_doc,
                                      end_time,
                                      graph=APPLICATION_GRAPH):
    query_template = Template("""
PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX sh: <http://mu.semte.ch/vocabularies/ext/signinghub/>

INSERT {
    GRAPH $graph {
        ?signing_wrap_up a prov:Activity ;
            dct:type $wrap_up_type ;
            prov:wasInformedBy ?signing ;
            dossier:Activiteit.einddatum $end_time ;
            prov:generated $signed_doc .
    }
}
WHERE {
    GRAPH $graph {
        ?signing_prep a prov:Activity ;
            dct:type $prep_type ;
            sh:document ?sh_doc .
        ?sh_doc sh:packageId $sh_package_id ;
            sh:documentId $sh_document_id .
        ?signing a prov:Activity ;
            dct:type $sig_type ;
            prov:wasInformedBy ?signing_prep .
    }
}
""")
    return query_template.substitute(
        graph=sparql_escape_uri(graph),
        prep_type=sparql_escape_uri(SIGNING_PREP_ACT_TYPE_URI),
        sig_type=sparql_escape_uri(SIGNING_ACT_TYPE_URI),
        wrap_up_type=sparql_escape_uri(SIGNING_WRAP_TYPE_URI),
        sh_package_id=sparql_escape_string(sh_package_id),
        sh_document_id=sparql_escape_string(sh_document_id),
        signed_doc=sparql_escape_uri(signed_doc),
        end_time=sparql_escape_datetime(end_time))

def construct_get_wrap_up_activity(sh_package_id,
                                   graph=APPLICATION_GRAPH):
    query_template = Template("""
PREFIX dossier: <https://data.vlaanderen.be/ns/dossier#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX sh: <http://mu.semte.ch/vocabularies/ext/signinghub/>

SELECT DISTINCT(?signing_wrap_up AS ?uri) ?signed_doc
WHERE {
    GRAPH $graph {
        ?signing_prep a prov:Activity ;
            dct:type $prep_type ;
            sh:document ?sh_doc .
        ?sh_doc sh:packageId $sh_package_id .
        ?signing a prov:Activity ;
            dct:type $type ;
            prov:wasInformedBy ?signing_prep .
        ?signing_wrap_up a prov:Activity ;
            dct:type $wrap_up_type ;
            prov:generated ?signed_doc .
        ?signed_doc a dossier:Stuk .
    }
}
""")
    return query_template.substitute(
        graph=sparql_escape_uri(graph),
        prep_type=sparql_escape_uri(SIGNING_PREP_ACT_TYPE_URI),
        sig_type=sparql_escape_uri(SIGNING_ACT_TYPE_URI),
        wrap_up_type=sparql_escape_uri(SIGNING_WRAP_TYPE_URI),
        sh_package_id=sparql_escape_string(sh_package_id))
