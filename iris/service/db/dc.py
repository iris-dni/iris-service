import pytz
import datetime
import dateutil.parser


def iso_now():
    return time_now_offset().isoformat()


def iso_now_offset(offset=None):
    def do():
        return time_now_offset().isoformat()
    return do


def time_now():
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.UTC)
    return utc


def time_now_offset(offset=None):
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.UTC)
    if offset is not None:
        utc += offset
    return utc


DC_CREATED = 'created'
DC_MODIFIED = 'modified'
DC_EFFECTIVE = 'effective'
DC_EXPIRES = 'expires'

DC_DEFAULT = {
    DC_MODIFIED: iso_now,
    DC_CREATED: iso_now,
    DC_EFFECTIVE: None,
    DC_EXPIRES: None,
}

DC_TIME_PROPERTIES = set([
    DC_MODIFIED,
    DC_CREATED,
    DC_EFFECTIVE,
    DC_EXPIRES,
])


def dc_defaults(*args, **kwargs):
    def defaults():
        result = {}
        for key in args:
            if key not in DC_DEFAULT:
                raise KeyError('dc key "%s" not allowed' % key)
            kwargs[key] = DC_DEFAULT[key]
        for key, value in kwargs.items():
            if key not in DC_DEFAULT:
                raise KeyError('dc key "%s" not allowed' % key)
            if hasattr(value, '__call__'):
                value = value()
            result[key] = value
        return result
    return defaults


def dc_defaults_all():
    return dc_defaults(**DC_DEFAULT)


def dc_update(doc, **kwargs):
    dc = doc.dc
    for key, value in kwargs.items():
        if key not in DC_DEFAULT:
            raise KeyError('dc key "%s" not allowed' % key)
        if hasattr(value, '__call__'):
            value = value()
        dc[key] = value
    return dc


def dc_time(doc):
    """Provide an object containing the dc time properties as datetime objects
    """
    dc = doc.dc
    result = {}
    for key, value in dc.items():
        if not value:
            result[key] = value
        elif key in DC_TIME_PROPERTIES:
            result[key] = dateutil.parser.parse(value)
    return result
