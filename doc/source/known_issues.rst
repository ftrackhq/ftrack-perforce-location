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
