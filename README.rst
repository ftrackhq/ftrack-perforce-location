########################
ftrack perforce location
########################

ftrack-perforce-location allows ftrack to publish to and import from a Perforce
depot through a user's local workspace.

It demonstrates using an accessor, location, resrouce transformer and structure
to ingest, track versions of files and assets. For more information how ftrack
manages files, see:
https://help.ftrack.com/developing-with-ftrack/key-concepts/locations
https://help.ftrack.com/administering-ftrack/general/configuring-file-storage

Prerequisites
================
Perforce
--------
* Ensure that a Perforce server is available and reachable.
* Ensure that a user is registered to the Perforce server.
* Ensure that the user has created a workspace on their machine.

ftrack
------
* Revert to the default centralized storage scenario.

Building the plugin
===================

.. code:: bash

    $ python setup.py build_plugin

TODO
====
* Import file published
* Configure Perforce user ui

Known issues
============
* User must login to Perforce themselves, either on command line as below, or
  with another client.::

    $ p4 login

* In case of :: [Warning]: '<FILEPATH> - file(s) not in client view.'#

.. code::bash

    $p4 client <yourclient>

and ensure :

.. code::config

    View:
    //depot/... //<yourclient>/...



Configuration
=============

Perforce configuration is locally stored in perforce_config.json, inside the
ftrack-connect settings directory. The fist time this plugin is run, the
settings file will be created and an error raised if the config is empty.

Please manually edit the file to include:

* **host** , the hostname to identify as.
* **port** , server address (e.g. ssl:1666). Format: [protocol:][address:]port
* **user** , your Perforce user.
* **password** , your Perforce password.
* **using_workspace** , the Perforce workspace to be used.
* **workspace_root** , the root of the workspace.


