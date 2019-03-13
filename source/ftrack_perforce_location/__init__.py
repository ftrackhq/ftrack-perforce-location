# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging

from P4 import P4

from ftrack_perforce_location.configure_logging import configure_logging

configure_logging(__name__)
P4.logger = logging.getLogger(__name__)
