..
    :copyright: Copyright (c) 2015 ftrack

.. _installing:

Building from source
====================

You can also build manually from the source for more control. First obtain a
copy of the source by either downloading the
`zipball <https://bitbucket.org/ftrack/ftrack-perforce-location/get/master.zip>`_ or
cloning the public repository::

    git clone git@bitbucket.org:ftrack/ftrack-perforce-location.git

Then you can build and install the package into your current Python
site-packages folder::

    python setup.py build_plugin

The result plugin will then be available under the build folder.
Copy or symlink the result plugin folder in your FTRACK_CONNECT_PLUGIN_PATH.


Building documentation from source
----------------------------------

To build the documentation from source::

    python setup.py build_sphinx

Then view in your browser::

    file:///path/to/ftrack-perforce-location/build/doc/html/index.html
