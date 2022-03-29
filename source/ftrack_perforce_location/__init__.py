# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging
import os
import sys
from ftrack_perforce_location.configure_logging import configure_logging

configure_logging(__name__)

import P4

from ftrack_perforce_location._version import __version__

P4.logger = logging.getLogger(__name__)
