from .rest.service import RESTService
from lovely.pyrest import rest


rest.RestService("petition_admin_api")(RESTService)


def includeme(config):
    #
    # The generic admin data access endpoint
    #   Allows acces to `/admin/<mapper>`
    #
    config.add_route('petition_admin_api',
                     '/admin/petitions',
                     static=True)
