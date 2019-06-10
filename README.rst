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

ftrack
------
* Configure the Perforce Storage Scenario with your Perforce server protocol,
address and port.

Building the plugin
===================

.. code:: bash

    $ python setup.py build_plugin

TODO
====
* Import file published

Known issues
============
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
settings file will be created, and the following attributes will be read from
Perforce if available. They may need to be set manually if no environment
variables or Perforce config files are setup.

* **user** , your Perforce user.
* **using_workspace** , the Perforce workspace to be used.
* **workspace_root** , the root of the workspace.
