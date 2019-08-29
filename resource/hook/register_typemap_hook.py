import ftrack_api

# Binary formats
BINARY = 'binary'
BINARYFL = 'binary+Fl'
BINARYW = 'binary+w'
BINARYL = 'binary+l'
BINARYLS = 'binary+lS'

# Ascii formats
TEXT = 'text'
TEXTL = 'text+l'


def register_images_typemap(event):
    return {
        '.bmp': BINARY,
        '.jpg': BINARYL,
        '.tga': BINARYL
    }

def register_autodesk_typemap(event):

    return {
        '.abc': BINARYL,
        '.fbx': BINARYL,
        '.mb': BINARYL,
        '.ma': TEXTL,
        '.max': BINARYL,
        '.pdb': BINARY,
    }


def register_adobe_typemap(event):

    return {
        '.prproj', BINARYFL,
        '.psd': BINARYFL,
        '.ai': BINARYFL,
        '.aep': BINARYFL
    }


def register_unreal_typemap(event):
    # https://docs.unrealengine.com/en-US/Engine/Basics/SourceControl/Perforce/index.html
    return {
        '.app': BINARYW,
        '.c': TEXT,
        '.config': TEXT,
        '.cpp': TEXT,
        '.cs': TEXT,
        '.dll': BINARYW,
        '.dylib': BINARYW,
        '.exe': BINARYW,
        '.ipa': BINARYW,
        '.ini': TEXT,
        '.lib': BINARYW,
        '.h': TEXT,
        '.m': TEXT,
        '.mm': TEXT,
        '.py': TEXT,
        '.stub': BINARYW,
        '.uasset': BINARYL,
        '.umap': BINARYL,
        '.upk': BINARYL,
        '.udk': BINARYL
}

def register_unity_typemap(event):
    # https://community.perforce.com/s/article/15244
    return {
        '.asset': BINARYL,
        '.aas': BINARYL,
        '.cm': TEXTL,
        '.cs': TEXT,
        '.dll': BINARY,
        '.exe': BINARY,
        '.ini': BINARY,
        '.ip': BINARY,
        '.js': TEXT,
        '.lib': BINARY,
        '.mat': BINARYL,
        '.md5anim': TEXTL,
        '.md5mesh': TEXTL,
        '.meta': TEXT,
        '.mp3': BINARYL,
        '.prefab': BINARYL,
        '.proc': TEXTL,
        '.psb': BINARYL,
        '.response': BINARY,
        '.shader': TEXT,
        '.stub': BINARY,
        '.u': BINARY,
        '.unity': BINARYL,
    }



def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    # IMAGES
    api_object.event_hub.subscribe(
        'topic=ftrack.perforce.typemap.register',
        register_images_typemap
    )

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