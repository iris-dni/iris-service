
def includeme(config):
    config.add_route('ogcheck',
                     '/og/check',
                     static=True)
