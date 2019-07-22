import os
import sys


def import_p4():
    cwd = os.path.dirname(__file__)
    p4_modules = os.path.abspath(os.path.join(cwd, '..', '..', 'modules'))
    modules = os.listdir(p4_modules)
    for module in modules:
        full_path = os.path.join(p4_modules, module)
        if full_path not in sys.path:
            sys.path.append(full_path)
        try:
            # attempt to import P4
            from P4 import P4
        except Exception as error:
            # failed to load so lets remove it from the path!
            if sys.path[-1] == full_path:
                del sys.path[-1]
        else:
            print 'SUCCESSFULLY LOADED', full_path
            break
