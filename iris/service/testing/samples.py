import random
from datetime import datetime

from faker import Faker

from iris.service.user import User
from iris.service.petition import Petition
from iris.service.petition.document import StateContainer
from iris.service.city import City


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


def petitions(amount, seed='0'):
    faker = Faker()
    faker.seed(seed)
    random.seed(seed)
    for i in range(amount):
        time = faker.date_time_between_dates(
            datetime_start=datetime(2016, 1, 1),
            datetime_end=datetime(2016, 7, 21),
            tzinfo=None,
        )
        create_object(Petition,
                      state=StateContainer(
                          name=random.choice(['draft', 'active', 'pending'])
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
                      supporters={
                          'amount': random.randint(0, 20),
                          'required': 10
                      },
                     )
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
