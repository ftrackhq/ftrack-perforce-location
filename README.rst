ftrack-perforce-location
========================

In this repo is hosted the code for allowing ftrack to seamlessly publish in perforce.


pre flight check
================

perforce
--------

* ensure perforce server is available and recheable.
* ensure a user is registered to the perforce server.


ftrack
------
* disable storage scenario


building the plugin
===================

.. code::

    $ python setup.py build_plugin

TODO
====

* import file published
* configure perforce user ui

known issues
============

* login to perforce currently required from command line: 

.. code::
    
    $ p4 login

configuration
=============

Perforce configuration is locally stored next to ftrack-connect settings.
The fist time this plugin will run the settings file will be created and an error raised
if the config is empty.

please manually edit the file to include:

* **server** , the perforce server name.
* **port** , the perforce server port (usually ssl:1666).
* **user** , your perforce user.
* **password** , your perforce password.
* **using_workspace** , the perforce workspace to be used.
* **workspace_root** , the root of the workspace.