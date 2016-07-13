
def includeme(config):
    #
    # The public petition endpoints
    #
    config.add_route('petition_public_api',
                     'petitions',
                     static=True)
