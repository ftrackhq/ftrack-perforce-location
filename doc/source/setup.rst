Users permissions
=================

.. note::

    This is has to be performed by a perforce user with `Admin rights <https://www.perforce.com/manuals/v15.1/p4sag/chapter.protections.html>`_.

* In **p4admin** : Create users with name as the **same login name as ftrack**
* In **p4admin** : Ensure users are part of the **p4users group as Members and Owners**

.. image:: /image/user-permissions.png


Workspace and local folder
==========================

Local folder
------------

Create a workspace folder on local disk where to perforce will checkout file to.


For example::

    C:\Users\loren\OneDrive\Documents\PerforceWS


Workspace
---------

Create workspace
................

In **p4v**: login with your current ftrack username and perforce password.
Create a new workspace

.. image:: /image/new-workspace.png


Set workspace
.............

Set the workspace path to the previously created folder

.. image:: /image/workspace-setup.png



Once done this how should look like in p4v

.. image:: /image/workspace-setup-done.png


Integration
===========

Setup user workspace and credentials
------------------------------------

#. `Download <https://www.ftrack.com/en/portfolio/perforce>`_ or `build the latest <https://bitbucket.org/ftrack/ftrack-perforce-location/src>`_ integration.
#. `Install the integration <https://help.ftrack.com/en/articles/3504354-ftrack-connect-plugins-discovery-installation-and-update>`_ as ftrack plugin
#. Start connect.

If the plugin is properly installed you should see the Configure Perforce User action.

.. image:: /image/connect-startup.png

You can now launch the **Configure Perforce User action** and select the workspace to use and click save settings.


.. image:: /image/user-setup-workspace-connect.png


.. note::

    If you haven’t been logging into perforce for sometime, a login in window will show up asking for username and password.

    .. image:: /image/reenter-pass.png


The workspace root should match the folder created and setup during the perforce user configuration.

.. image:: /image/user-setup-workspace-connect-done.png


This will result in a configuration file written in the ftrack-connect data folder, containing the chosen settings :

.. image:: /image/config-result.png

Project Configuration
=====================

.. note::

    For this action to appear and run, the user running it should be having super `Access Level <https://www.perforce.com/manuals/v15.1/p4sag/chapter.protections.html>`_ assigned from perforce itself
    and the `right permissions on the ftrack server <https://help.ftrack.com/en/articles/1040544-managing-permissions-and-roles>`_ to add custom attributes.

    .. image:: /image/permissions.png



On the designed project , run actions and select **Configure Project Perforce**.

.. image:: /image/configure-project-action.png

Set the per project depot attribute and click Submit

.. image:: /image/per-project-depot.png

To confirm all is in place **run p4v** and check the view to the current project has been correctly added

.. image:: /image/view-configuragion.png


Publishing
==========

You should now be able to publish to perforce using connect as usual using connect or any other ftrack integration.

.. image:: /image/connect-publish.png

This should result in connect reporting the successful publish

.. image:: /image/connect-publish-result.png

On the server , the component should be added to the **ftrack.perforce-scenario** location.

.. image:: /image/connect-publish-result-server.png

Running p4v should show the files in the depot.

.. image:: /image/p4v-successful-publish.png


