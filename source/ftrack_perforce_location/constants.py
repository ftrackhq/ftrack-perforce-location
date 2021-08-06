# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import os

SCENARIO_ID = 'ftrack.perforce-scenario'
SCENARIO_LABEL = 'Perforce storage scenario'
SCENARIO_DESCRIPTION = (
    'Storage scenario where files are stored and versioned by '
    'Perforce, with flexible mapping between projects and depots.'
)
ICON_URL = os.environ.get('FTRACK_SERVER', '') + '/application_icons/helix_core.png'
