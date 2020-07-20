import os
import sys
import logging

logger = logging.getLogger(__name__)

os_mapping = {
    'win32': 'windows',
    'darwin': 'osx',
    'linux2': 'linux'
}


def import_p4():

    # if the module has already been loaded skip the checks.
    if 'P4' in sys.modules:
        # logger.debug('P4 module loaded: {}'.format(sys.modules['P4']))
        return

    cwd = os.path.dirname(__file__)
    p4_modules = os.path.abspath(os.path.join(cwd, '..', '..', 'modules', os_mapping[sys.platform]))
    modules = os.listdir(p4_modules)
    for module in modules:

        full_path = os.path.join(p4_modules, module)
        logger.debug('Looking for module in path: {}'.format(full_path))
        if full_path not in sys.path:
            sys.path.append(full_path)
        try:
            # attempt to import P4
            from P4 import P4 as _P4test, P4Exception as _P4ExceptionTest
        except Exception as error:
            # failed to load so lets remove it from the path!
            if sys.path[-1] == full_path:
                del sys.path[-1]
        else:
            logger.debug('Successfully loaded module from {}'.format(full_path))
            break
