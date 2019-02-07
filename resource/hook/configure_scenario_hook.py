# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import sys
import logging
import ftrack_api

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)


from ftrack_perforce_location.scenario import ConfigurePerforceStorageScenario


logger = logging.getLogger(
    'ftrack_perforce_location.configure_scenario_hook'
)


def register(session):
    '''Register storage scenario.'''
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.info('discovering configure storage scenario')
    scenario = ConfigurePerforceStorageScenario()
    scenario.register(session)
