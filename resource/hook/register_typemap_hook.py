import ftrack_api

BINARY = 'binary'
BINARYF = 'binary+Fl'
BINARYW = 'binary+w'
BINARYL = 'binary+l'
BINARYLS = 'binary+lS'

TEXT = 'text'
TEXTL = 'text+l'


def register_autodesk_typemap(event):

    return {
        '.mb': BINARYL,
        '.ma': TEXTL,
        '.pdb': BINARY,
        '.abc': BINARYL,
        '.fbx': BINARYL,
        '.max': BINARYL
    }


def register_adobe_typemap(event):

    return {
        '.psd': BINARYF,
        '.ai': BINARYF,
        '.aep': BINARYF
    }


def register_unreal_typemap(event):
    # https://docs.unrealengine.com/en-US/Engine/Basics/SourceControl/Perforce/index.html
    return {
        '.exe': BINARYW,
        '.dll': BINARYW,
        '.lib': BINARYW,
        '.app': BINARYW,
        '.dylib': BINARYW,
        '.stub': BINARYW,
        '.ipa': BINARYW,
        '.bmp': BINARY,
        '.ini': TEXT,
        '.config': TEXT,
        '.cpp': TEXT,
        '.h': TEXT,
        '.c': TEXT,
        '.cs': TEXT,
        '.m': TEXT,
        '.mm': TEXT,
        '.py': TEXT,
        '.uasset': BINARYL,
        '.umap': BINARYL,
        '.upk': BINARYL,
        '.udk': BINARYL
}

def register_unity_typemap(event):
    # https://community.perforce.com/s/article/15244
    return {
        '.js': TEXT,
        '.cs': TEXT,
        '.shader': TEXT,
        '.meta': TEXT,
        '.cm': TEXTL,
        '.proc': TEXTL,
        '.md5mesh': TEXTL,
        '.md5anim': TEXTL
    }



def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    # AUTODESK
    api_object.event_hub.subscribe(
        'topic=ftrack.perforce.typemap.register',
        register_autodesk_typemap
    )

    # ADOBE
    api_object.event_hub.subscribe(
        'topic=ftrack.perforce.typemap.register',
        register_adobe_typemap
    )

    # UNREAL
    api_object.event_hub.subscribe(
        'topic=ftrack.perforce.typemap.register',
        register_unreal_typemap
    )

    # UNITY
    api_object.event_hub.subscribe(
        'topic=ftrack.perforce.typemap.register',
        register_unity_typemap
    )