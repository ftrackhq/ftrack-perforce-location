import ftrack_api


def register_typemap(event):
    return {'Foo': 'bar'}


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    # Location will be available from actions
    api_object.event_hub.subscribe(
        'topic=ftrack.perforce.typemap.register',
        register_typemap
    )