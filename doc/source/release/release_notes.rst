..
    :copyright: Copyright (c) 2019 ftrack

.. _release/release_notes:

*************
Release Notes
*************

.. release :: Upcoming

    .. change:: add

        Discover new icon from ftrack server.

.. release:: 0.7.0
    :date: 2019-11-04

    .. change:: changed

        Split hooks and events, so the location can be imported from api only.

        .. note::
           In order to use it only with the session, please set env::FTRACK_EVENT_PLUGIN_PATH
           to the **location** folder before starting the session.

    ..change:: changed
        :tags: Setup

        Pip compatibility for version 19.3.0 or higher

    .. change:: changed

        Defer the Qt import when loading scenario.

    .. change:: new

        Use Qt.py instead of the bundled QtExt with Connect.

    .. change:: new

        Support publish of file sequences.

    .. change:: fixed

        Perforce modules cannot be imported and used in DCC applications.

    .. change:: add

        Provide default file encode mapping based on the file extension.

    .. change:: new

        Enforce perforce username to be the same as the ftrack user logged in.


.. release:: 0.1.0
    :date: 2019-05-21

    .. change:: fixed
        :tags: action

        User settings crashes under osx and windows platform.

    .. change:: fixed
        :tags: login

        Perforce password is not properly set.

    .. change:: fixed
        :tags: workspace

        Workspaces breaks if contains spaces.

    .. change:: new
        :tags: permission

        Admin role for action gets checked against perforce roles too.

    .. change:: new
        :tags: workspace

        User's workspace is created on first run if not already available.

    .. change:: new
        :tags: docs

        Init documentation.
