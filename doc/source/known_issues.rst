Known issues
============

File not in view
----------------

Cause
.....

The view of the project depot has not been properly added to the p4 configuration for the current user.

Error
.....
This means the view perforce is referring to , which is the project is not been mapped correctly.


.. image:: /image/publish-view-error.png



Solution
........

* Remove the custom attribute from the web ui and re run the configure project action.
* Ensure the view is part of the current perforce's user configuration

.. image:: /image/config-view.png
