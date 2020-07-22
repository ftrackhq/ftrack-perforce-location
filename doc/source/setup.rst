
Users permissions
=================

.. note::

    This is has to be performed by a perforce user with **`Admin rights <https://www.perforce.com/manuals/v15.1/p4sag/chapter.protections.html>`_**.

* In **p4admin** : Create users with name as the **same login name as ftrack**
* In **p4admin** : Ensure users are part of the **p4users group as Members and Owners**

.. image:: image/user-permissions.png


Workspace and local folder
==========================

Local folder
------------

Create a workspace folder on your local disk as a location to save and store files


For example::

    C:\Users\loren\OneDrive\Documents\PerforceWS


Workspace
---------

Create workspace
................

In **p4v**: login with your current ftrack username and perforce password.
Create a new workspace

.. image:: image/new-workspace.png


Set workspace
.............

Set the workspace path to the folder created in step 1 of this process:


.. image:: image/workspace-setup.png



Once complete, p4v should look like this:

.. image:: image/workspace-setup-done.png


Integration
===========

Setup user workspace and credentials
------------------------------------

#. `Download <https://www.ftrack.com/en/portfolio/perforce>`_ or `build the latest <https://bitbucket.org/ftrack/ftrack-perforce-location/src>`_ integration.
#. `Install the integration <https://help.ftrack.com/en/articles/3504354-ftrack-connect-plugins-discovery-installation-and-update>`_ as ftrack plugin
#. Start connect.

If the plugin is properly installed you should see the Configure Perforce User action.

.. image:: image/connect-startup.png

Launch the Configure Perforce User Action from ftrack Connect. Select the workspace you wish to use and click ‘save settings’.

.. image:: image/user-setup-workspace-connect.png


.. note::

    A login window will display and ask for a username and password, if you have not logged into Perforce for a while.

    .. image:: image/reenter-pass.png


Your ‘Workspace Root’ should match that of the folder created and set up during the Perforce user configuration.
(See: Set up user workspace.)

.. image:: image/user-setup-workspace-connect-done.png


This will write a configuration file into the ftrack-connect data folder, which will contain your chosen settings:

.. image:: image/config-result.png


You can now restart ftrack connect.


Project Configuration
=====================

.. note::

    The user must be assigned super `Access Level <https://www.perforce.com/manuals/v15.1/p4sag/chapter.protections.html>`_  in Perforce and be granted
    `permissions <https://help.ftrack.com/en/articles/1040544-managing-permissions-and-roles>`_ to add custom attributes on the ftrack server,
    otherwise this Action will not appear and run.


    .. image:: image/permissions.png


Run ftrack Actions and select Configure Project Perforce on the created project.

.. image:: image/configure-project-action.png

Set the per project depot attribute and click Submit

.. image:: image/per-project-depot.png

To confirm all is in place **run p4v** and check the view to the current project has been correctly added

.. image:: image/view-configuration.png

You can now restart connect.


Publishing
==========

You should now be able to publish to perforce using connect as usual using connect or any other ftrack integration.

.. image:: image/connect-publish.png

This will result in ftrack Connect reporting a successful publish:

.. image:: image/connect-publish-result.png

The component will be added to the server’s **ftrack.perforce-scenario** location.

.. image:: image/connect-publish-result-server.png

Running p4v should show the files in the depot.

.. image:: image/p4v-successful-publish.png


