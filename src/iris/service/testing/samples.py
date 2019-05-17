import random
from datetime import datetime

from faker import Faker

from iris.service.content.user import User
from iris.service.content.petition import Petition
from iris.service.content.petition.document import Supporter
from iris.service.content.petition.document import StateContainer
from iris.service.content.city import City


def create_object(cls, *args, **kwargs):
    obj = cls(*args, **kwargs)
    obj.store()
    return obj


def users(amount, seed='0'):
    faker = Faker()
    faker.seed(seed)
    random.seed(seed)
    for i in range(amount):
        role = random.choice([None, 'admin'])
        if role is None:
            role = []
        else:
            role = [role]
        time = faker.date_time_between_dates(
            datetime_start=datetime(2016, 1, 1),
            datetime_end=datetime(2016, 7, 21),
            tzinfo=None,
        )
        provider = random.choice([None, 'azMedien', 'zeitOnline'])
        sso = []
        if provider:
            sso = [
                {
                    'provider': provider,
                    'trusted': bool(random.getrandbits(1))
                }
            ]
        create_object(User,
                      state=random.choice(['active', 'disabled']),
                      roles=role,
                      email=faker.email(),
                      firstname=faker.first_name(),
                      lastname=faker.last_name(),
                      dc={
                          'created': time,
                          'modified': time,
                      },
                      sso=sso,
                     )
    User.refresh()


def petitions(amount, seed='0', timerange=None):
    faker = Faker()
    faker.seed(seed)
    random.seed(seed)
    cities = City.search({"query": {"match_all": {}}, "size": 1000}
                        )['hits']['hits']
    users = User.search({"query": {"match_all": {}}, "size": 1000}
                       )['hits']['hits']
    if timerange is None:
        timerange = (
            datetime(2016, 1, 1),
            datetime(2016, 7, 21),
        )
    for i in range(amount):
        time = faker.date_time_between_dates(
            datetime_start=timerange[0],
            datetime_end=timerange[1],
            tzinfo=None,
        )
        state_parent, state_name = random.choice([
            ('', 'draft'),
            ('supportable', 'active'),
            ('supportable', 'pending')])
        city = random.choice(cities)
        owner = random.choice(users)
        petition = create_object(
            Petition,
            state=StateContainer(
                name=state_name,
                parent=state_parent,
                listable=state_name != 'draft',
                tick=state_parent == 'supportable' and state_name == 'active',
                letter_wait_expire=None,
            ),
            tags=[random.choice(['pet', 'shop', 'boys'])],
            title=faker.text(50),
            description='\n'.join(faker.paragraphs(5)),
            suggested_solution='\n'.join(faker.paragraphs(3)),
            dc={
                'created': time,
                'modified': time,
                'effective': None,
                'expires': None,
            },
            city=city.id,
            owner=owner.id,
            supporters={
                'amount': 0,
                'required': city.treshold
            },
        )
        if state_parent == 'supportable':
            for _ in range(0, random.randint(0, 20)):
                if bool(random.getrandbits(1)):
                    user = random.choice(users)
                    supporter = petition.addSupporter(request=None,
                                                      user_id=user.id)
                else:
                    data = {
                        "mobile": faker.phone_number(),
                        "firstname": faker.first_name(),
                        "lastname": faker.last_name(),
                    }
                    supporter = petition.addSupporter(request=None,
                                                      data=data)
                support_time = faker.date_time_between_dates(
                    datetime_start=time,
                    datetime_end=timerange[1],
                    tzinfo=None,
                )
                supporter.dc['created'] = support_time
                supporter.store()
    Supporter.refresh()
    Petition.refresh()


def cities(amount, seed='0'):
    faker = Faker()
    faker.seed(seed)
    random.seed(seed)
    for i in range(amount):
        time = faker.date_time_between_dates(
            datetime_start=datetime(2016, 1, 1),
            datetime_end=datetime(2016, 7, 21),
            tzinfo=None,
        )
        create_object(City,
                      id=i,
                      provider='test',
                      name=faker.city(),
                      tags=list(set([random.choice(['portal:aaz',
                                                    'portal:bzb',
                                                    'portal:gtb'])
                                     for i in range(random.randint(1, 3))]
                               )),
                      zips=list(set([faker.postalcode()
                                     for i in range(random.randint(1, 4))]
                               )),
                      treshold=10,
                      dc={
                          'created': time,
                          'modified': time,
                      },
                     )
    City.refresh()
