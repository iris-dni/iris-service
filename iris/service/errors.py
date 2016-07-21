from enum import Enum


class Errors(Enum):

    bad_request = 'Bad request: {message}'

    unauthenticated = 'This endpoint needs authentication'
    not_found = 'Not Found'
    forbidden = 'Access forbidden'
    mapper_not_found = 'Mapper "{mapperName}" not found'
    method_not_allowed = 'Method not allowed: {message}'
    property_required = 'Property "{property_name}" is required'

    document_not_found = (
        "Id '{contentId}' of content type '{mapperName}' not found"
    )
