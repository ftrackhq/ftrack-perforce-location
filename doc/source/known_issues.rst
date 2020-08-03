Known issues
============

File not in view
----------------

Cause
.....

The project depot view was incorrectly added to the p4 configuration for the current user.

Error
.....
The above means that the view Perforce is referring to (the project) is incorrectly mapped.


.. image:: /image/publish-view-error.PNG


Solution
........

* Remove the custom attribute from the web ui .
* Re run the configure project action.
* Ensure the view is part of the current perforce's user configuration.

.. image:: /image/config-view.PNG

Login timeout
-------------

Cause
.....

After some time, the perforce session time out and ask to be re connected.


Error
.....
    .. image:: image/wrong-pass.PNG


Solution
........

The default timeout is define on a per-group basis.
There are two options to fix this


1) set the timeout for the group to *unlimited* using **p4admin** or **p4 group** `command <https://www.perforce.com/perforce/r12.1/manuals/cmdref/group.html>`_
2) set the perforce credentials in system environment variables or using **p4 set** `command https://www.perforce.com/manuals/v17.1/cmdref/Content/CmdRef/p4_set.htm>`_::

    * P4PASSWD
    * P4USER

