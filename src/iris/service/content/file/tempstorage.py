import os

TEMP_DIR = "/tmp/iris-service"


def get_temp_upload_path():
    """Get the path for the upload directory and create it if needed.
    """
    path = os.path.join(TEMP_DIR, 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def store_temp_file(iid, file_obj):
    """Store the file locally in a temporary location.

    Used for local and testing environment.
    """
    filename = os.path.join(get_temp_upload_path(), iid)
    f = open(filename, 'w')
    f.write(file_obj.read())
    f.close()


def get_temp_file(iid):
    """Get a file stored locally in temporary location.

    Used for local and testing environment.
    """
    filename = os.path.join(get_temp_upload_path(), iid)
    return open(filename, 'r')


def includeme(config):
    global TEMP_DIR
    settings = config.get_settings()
    TEMP_DIR = settings.get('temp.dir', TEMP_DIR)
