import json


def termFilter(fieldname):
    def handleFilter(value):
        return {"term": {fieldname: value}}
    return handleFilter


def termsFilter(fieldname):
    """
    Transforms a comma separated list of keywords into a terms query object,
    which can be used by an ES search operation.

    raises a ValueError of no valid keyword is provided.
    """
    def handleFilter(value):
        if isinstance(value, (list, tuple)):
            keys = [v.strip() for v in value if v.strip()]
        else:
            keys = [v.strip() for v in value.split(',') if v.strip()]
        if keys:
            return {"terms": {fieldname: keys}}
        raise ValueError("No keywords provided")
    return handleFilter


BOOL_TRUE_VALUES = set([True, '1', 'true'])
BOOL_FALSE_VALUES = set([False, '0', 'false'])


def booleanFilter(fieldname):
    def handleFilter(value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in BOOL_TRUE_VALUES:
            value = True
        elif value in BOOL_FALSE_VALUES:
            value = False
        else:
            raise ValueError(
                'Filter for "%s": "%s" invalid value' % (
                    fieldname, value))
        return {"term": {fieldname: value}}
    return handleFilter


def genericTermsQuery(value):
    """Builds a terms query

    value must contain a JSON string containing an object:
        {
            "operator": "<and|or>",
            "fields": {
                "name_1": [<values>],
                "name_2": [<values>],
                ...
            }
        }
    """
    OPERATORS = {
        'or': 'should',
        'and': 'must'
    }
    data = json.loads(value)
    operator = data.get('operator', 'or').lower()
    if operator not in OPERATORS.keys():
        raise ValueError('Operator must be "and" or "or" is "%s"' % operator)
    fields = data.get('fields', [])
    if not fields:
        raise ValueError('No fields provided')
    queries = []
    for name, values in fields.iteritems():
        queries.append(termsFilter(name)(values))
    return {
        "bool": {
            OPERATORS[operator]: queries
        }
    }


def rangeFilter(field, operators=('gte', 'lt')):
    def handleFilter(value):
        operations = {}
        for i, op in enumerate(operators):
            if i > len(value):
                break
            v = value[i]
            if v:
                operations[op] = v
        return {
            "range": {
                field: operations
            }
        }
    return handleFilter


def fulltextQuery(fields, cutoff_frequency=None):
    """Build a fulltext search query

    Creates a `multi_match` query for the list of `fields` provided.
    If a `cutoff_frequency` is given it will be added to the query.
    """
    def handleParameter(value):
        value = value.strip()
        if not value:
            raise ValueError("No query string provided")
        result = {
            "multi_match": {
                "query": value,
                "fields": fields
                }
            }
        if cutoff_frequency is not None:
            result['multi_match']['cutoff_frequency'] = cutoff_frequency
        return result
    return handleParameter


def scoreSorter(order):
    """Sort by score value
    """
    if order == 'asc':
        return "_score"
    return {"_score": {"order": "asc"}}


def fieldSorter(fieldname, forcedOrder=None):
    """Sort a field

    A generic sorter which allows to define a field for sorting.

    If forcedOrder is not None it will be used as the sort order.
    """
    def handleSort(order):
        if forcedOrder is not None:
            order = forcedOrder
        return {fieldname: {"order": order}}
    return handleSort
