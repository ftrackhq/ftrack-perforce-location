from P4 import P4
import logging
from ftrack_perforce_location.configure_logging import configure_logging

configure_logging('ftrack_perforce_location')
P4.logger = logging.getLogger('ftrack_perforce_location')

