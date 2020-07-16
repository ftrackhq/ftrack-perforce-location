# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import logging
import os
import sys

import ftrack_api

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

from ftrack_perforce_location.scenario import ActivatePerforceStorageScenario


logger = logging.getLogger(
    'ftrack_perforce_location.activate_scenario_hook'
)


def register(session):
    '''Register storage scenario.'''
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.info('Discovering activate storage scenario')
    scenario = ActivatePerforceStorageScenario()
    scenario.register(session)
