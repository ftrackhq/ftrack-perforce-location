# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import re
import shutil
import sys
from pip._internal import main as pip_main  # pip >= 10

from setuptools import setup, find_packages, Command


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
BUILD_PATH = os.path.join(ROOT_PATH, 'build')
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.rst')
RESOURCE_PATH = os.path.join(ROOT_PATH, 'resource')
HOOK_PATH = os.path.join(RESOURCE_PATH, 'hook')
MODULES_PATH = os.path.join(RESOURCE_PATH, 'modules')

# Read version from source.
with open(os.path.join(
    SOURCE_PATH, 'ftrack_perforce_location', '_version.py'
)) as _version_file:
    VERSION = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)


STAGING_PATH = os.path.join(
    BUILD_PATH, 'ftrack-perforce-location-{0}'.format(VERSION)
)


class BuildPlugin(Command):
    '''Build plugin.'''

    description = 'Download dependencies and build plugin .'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Run the build step.'''
        # Clean staging path
        shutil.rmtree(STAGING_PATH, ignore_errors=True)

        # Copy hook files
        shutil.copytree(
            HOOK_PATH,
            os.path.join(STAGING_PATH, 'hook')
        )

        # Copy modules
        shutil.copytree(
            MODULES_PATH,
            os.path.join(STAGING_PATH, 'modules')
        )

        pip_main(
            [
                'install',
                '.',
                '--target',
                os.path.join(STAGING_PATH, 'dependencies'),
                '--process-dependency-links'
            ]
        )

        result_path = shutil.make_archive(
            os.path.join(
                BUILD_PATH,
                'ftrack-perforce-location-{0}'.format(VERSION)
            ),
            'zip',
            STAGING_PATH
        )


# Call main setup.
setup(
    name='ftrack-perforce-location',
    version=VERSION,
    description='ftrack location integration with perforce.',
    long_description=open(README_PATH).read(),
    keywords='ftrack, integration, connect, location, structure, accessor, perforce',
    url='https://bitbucket.org/ftrack/ftrack-perforce-location',
    author='ftrack',
    author_email='support@ftrack.com',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={
        '': 'source'
    },
    setup_requires=[
        'sphinx >= 1.2.2, < 2',
        'sphinx_rtd_theme >= 0.1.6, < 1',
        'lowdown >= 0.1.0, < 2'
    ],
    install_requires=[
        'appdirs == 1.4.0',
        'ftrack-action-handler',
        'qt.py >=1.0.0, < 2'
    ],
    tests_require=[
    ],
    zip_safe=False,
    cmdclass={
        'build_plugin': BuildPlugin,

    },
)
