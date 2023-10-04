..
    :copyright: Copyright (c) 2015 ftrack

.. _installing:

Building from source
====================

You can also build manually from the source for more control. First obtain a
copy of the source by either downloading the
`zipball <https://bitbucket.org/ftrack/ftrack-perforce-location/get/master.zip>`_ or
cloning the public repository::

    git clone git@github.com:ftrackhq/ftrack-perforce-location.git

You can then `build and install <https://help.ftrack.com/en/articles/3504354-ftrack-connect-plugins-discovery-installation-and-update>`_ the plugin::

    python setup.py build_plugin

The result plugin will then be available under the build folder.
Copy or symlink the result plugin folder in your :envvar:`FTRACK_CONNECT_PLUGIN_PATH`.


standalone location
-------------------

In case you want to use this location as standalone (without connect running), please remember to set
:envvar:`FTRACK_EVENT_PLUGIN_PATH` to the **location** folder under the plugin root.

.. note::

    In order to authenticate to perforce please use:

    .. code::

        p4 -u <your username> login




Building documentation from source
----------------------------------

To build the documentation from source::

    python setup.py build_sphinx

Then view in your browser::

    file:///path/to/ftrack-perforce-location/build/doc/html/index.html
