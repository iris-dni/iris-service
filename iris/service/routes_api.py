
def includeme(config):
    #
    # The generic admin data access endpoint
    #   Allows acces to `/admin/<mapper>`
    #
    config.add_route('generic_rest_service',
                     '/admin',
                     static=True)
