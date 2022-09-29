# ftrack perforce location


ftrack-perforce-location allows ftrack to publish to and import from a
Perforce depot through a user\'s local workspace.

# Prerequisites

## Perforce

-   Ensure that a Perforce server is available and reachable.
-   Ensure that a user is registered to the Perforce server.

## ftrack

* Configure the Perforce Storage Scenario with your Perforce server
protocol, address and port.

# Documentation

Full documentation, including installation and setup guides, can be
found at <https://ftrack-perforce-location.readthedocs.io/en/latest/>

### Building the plugin

bash

$ python setup.py build_plugin

### Configuration

Perforce configuration is locally stored in perforce_config.json, inside
the ftrack-connect settings directory. The fist time this plugin is run,
the settings file will be created, and the following attributes will be
read from Perforce if available. They may need to be set manually if no
environment variables or Perforce config files are setup.

-   **user** , your Perforce user.
-   **using_workspace** , the Perforce workspace to be used.
-   **workspace_root** , the root of the workspace.
