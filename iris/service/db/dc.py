import pytz
import datetime


def now():
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.UTC)
    return utc.isoformat()


DC_DEFAULT = {
    'modified': now,
    'created': now,
    'effective': None,
    'expires': None,
}


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
