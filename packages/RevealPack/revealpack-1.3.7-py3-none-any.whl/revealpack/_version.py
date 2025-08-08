def get_version():
    # Return the static version from __init__
    from . import __version__
    return __version__

def get_description():
    from . import __description__
    return __description__ 