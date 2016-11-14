from iris.service import mail


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
    return data


def prepare_city(data):
    city = data['city']
    save_del(city, 'class')
    data = city['data']
    save_del(city, 'data')
    if data:
        save_del(data, ['_location', 'location', 'dc'])
        city.update(data)


def prepare_support(data):
    support = data['supporters']
    support['remaining'] = max(0, support['required'] - support['amount'])


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
