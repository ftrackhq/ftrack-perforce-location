import ftrack_api


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        return

    # TODO(spetterborg) Use structure instead
    from ftrack_perforce_location import perforce_location_plugin
    perforce_location_plugin.register(api_object)
