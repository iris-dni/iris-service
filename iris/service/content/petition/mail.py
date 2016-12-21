# -*- coding: utf-8 -*-
from iris.service import mail
from iris.service.content.petition.security import generate_petition_token


def send_petition_mail(request,
                       template,
                       petition,
                       users,
                       data={}
                       ):
    """Send a mail with a petition as context

    Prepares petition data for the mail and sends the mail.
    """
    mail_data = {
        'petition': prepare_petition(request, petition)
    }
    mail_data.update(data)
    return mail.send(template, users, mail_data)


def prepare_petition(request, petition):
    data = request.to_api(
        petition,
        resolve=['city'],
        extend=[])
    save_del(data,
             [
                 'state.object_json_pickle__',
                 'owner.class',
                 'owner.id',
             ]
            )
    prepare_support(data)
    prepare_city(data)
    data['urls'] = prepare_urls(petition)
    return data


def prepare_city(data):
    """Remove some properties and flatten out city data
    """
    city = data['city']
    save_del(city, 'class')
    data = city['data']
    save_del(city, 'data')
    if data:
        save_del(data, ['_location', 'location', 'dc'])
        city.update(data)


def prepare_support(data):
    """Add calculated fields to the supporters object
    """
    support = data['supporters']
    support['remaining'] = max(0, support['required'] - support['amount'])


def prepare_urls(petition):
    from iris.service.content.petition import SETTINGS
    replacements = {
        "id": petition.id,
        "token": generate_petition_token(petition),
    }
    city = petition.city()
    if city is not None:
        replacements['city_url_id'] = (normalize_name_for_url(city.name)
                                       + '-'
                                       + city.id)
    result = {}
    urls = SETTINGS['petition']['urls']
    for k, v in urls.iteritems():
        try:
            result[k] = v.format(**replacements)
        except KeyError:
            # A KeyError happens if a URL needs a replacement which is not
            # provided. This handler makes sure all URLs except the ones with
            # exceptions are provided.
            pass
    return result


def normalize_name_for_url(name):
    name = (name or '').lower()
    for old, new in ((u'ä', u'ae'),
                     (u'ö', u'oe'),
                     (u'ü', u'ue'),
                     (u'ß', u'sz'),
                     (u' ', u'_'),
                     (u'-', u'_'),
                    ):
        name = name.replace(old, new)
    return name


def save_del(data, name):
    """Save deep delete from a dict
    """
    if isinstance(name, list):
        for n in name:
            save_del(data, n)
        return
    parts = name.split('.', 1)
    if len(parts) == 1:
        n = parts[0]
        if isinstance(data, dict) and n in data:
            del data[n]
        return
    n, rest = parts
    if n not in data:
        return
    save_del(data[n], rest)
