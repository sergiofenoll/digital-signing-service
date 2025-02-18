import collections
from . import exceptions

def to_recs(result):
    bindings = result["results"]["bindings"]
    return [
        collections.defaultdict(
            lambda: None,
            [(k, v["value"]) for k, v in b.items()
        ])
    for b in bindings]

def to_answer(result):
    return result["boolean"]

def ensure_0_or_1(collection):
    if len(collection) > 1:
        raise exceptions.InvalidStateException(f"expected: 1 - found: {len(collection)}")
    elif len(collection) == 1:
        return collection[0]

def ensure_1(collection):
    if len(collection) != 1:
        raise exceptions.InvalidStateException(f"expected: 1 - found: {len(collection)}")
    return collection[0]

# TODO: below functions don't "escape" anything. Fix naming + consider added value
def sparql_escape_table(table):
    rows = ['(' + sparql_escape_list(row) + ')' for row in table]
    return '\n'.join(rows)

def sparql_escape_list(list):
    return ' '.join(list)
