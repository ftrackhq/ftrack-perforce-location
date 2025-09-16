import os
import logging
import importlib
import uuid
import sys


import ftrack_api


logging.basicConfig()
logger = logging.getLogger('ftrack_perforce_location')
logger.setLevel(logging.DEBUG)

plugins = [r"C:\\Users\\loren\\Documents\\devel\\solution delivery\\ftrack\\ftrack-perforce-location\\build\\ftrack-perforce-location-2.0.0-windows\\location"]
dependencies = os.path.join(plugins[0], '..', 'dependencies')
sys.path.append(dependencies)

# create session and fetch location
session = ftrack_api.Session(plugin_paths=plugins, auto_connect_event_hub=True)
location  = session.query('Location where name is "ftrack.perforce-scenario"').one()

# ensure location is properly composed
print(location)
print(location.structure)
print(location.accessor)
print(location.resource_identifier_transformer)
