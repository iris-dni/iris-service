from enum import Enum


class Errors(Enum):

    bad_request = 'Bad request: {message}'

    unauthenticated = 'This endpoint needs authentication'
    not_logged_in = 'Not logged in'
    not_found = 'Not Found'
    forbidden = 'Access forbidden'
    mapper_not_found = 'Mapper "{mapperName}" not found'
    method_not_allowed = 'Method not allowed: {message}'
    property_required = 'Property "{property_name}" is required'
    no_parameters = 'No parameters provided'
    too_many_parameters = 'Too many parameters provided'

    sso_invalid_data = 'Invalid SSO data'
    sso_unknown_api_key = 'Unknown api key'

    document_not_found = (
        "Id '{contentId}' for content type '{mapperName}' not found"
    )

    sm_transition_error = 'Transition error: {text}'
