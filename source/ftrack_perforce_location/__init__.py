# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os
import sys
from ftrack_perforce_location.import_p4api import import_p4

import_p4()
import P4

from ftrack_perforce_location.configure_logging import configure_logging
from ftrack_perforce_location._version import __version__

configure_logging(__name__)
P4.logger = logging.getLogger(__name__)
