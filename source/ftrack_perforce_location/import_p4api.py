import os
import sys


def import_p4():
    print 'TRYING TO IMPORT P4'
    cwd = os.path.dirname(__file__)
    p4_modules = os.path.abspath(os.path.join(cwd, '..', '..', 'modules'))
    print 'LOOKING IN PATH:', p4_modules
    modules = os.listdir(p4_modules)
    for module in modules:
        if module not in sys.path:
            print "ADDING", module, 'TO PATH'
            sys.path.append(module)

        try:
            # attempt to import P4
            print 'TRYING TO IMPORT....'
            from P4 import P4
        except:
            # failed to load so lets remove it from the path!
            print "FAILED TO IMPORT", module, "CLEANING UP PATH..."
            if sys.path[-1] == module:
                del sys.path[-1]
        else:
            break
