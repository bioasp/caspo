#!/usr/bin/env python

import shutil, os

from conda_build.metadata import MetaData
from conda_build.build import bldpkg_path

if __name__ == '__main__':
    artifacts_dir = 'artifacts'
    os.mkdir(artifacts_dir)

    meta = MetaData('recipe')
    shutil.copy(bldpkg_path(meta, m.config), artifacts_dir)
