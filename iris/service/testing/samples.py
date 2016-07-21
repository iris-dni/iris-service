import random
from datetime import datetime

from faker import Faker

from iris.service.user import User


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