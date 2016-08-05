#!/usr/bin/env python

import argparse, os, subprocess

from binstar_client.utils import get_binstar
import binstar_client.errors
import conda.config
from conda_build.metadata import MetaData


def artifact_already_exists(cli, meta, owner):
    """
    Checks to see whether the built recipe (aka distribution) already
    exists on the owner/user's binstar account.
    """
    distro_name = '{}/{}.tar.bz2'.format(conda.config.subdir, meta.dist())

    try:
        dist_info = cli.distribution(owner, meta.name(), meta.version(), distro_name)
    except binstar_client.errors.NotFound:
        dist_info = {}

    return bool(dist_info)

def upload(cli, meta, owner):
    try:
        with open('token', 'w') as fh:
            fh.write(cli.token)

        subprocess.check_call(['anaconda', '--quiet', '-t', 'token',
                               'upload', 'artifacts/{}.tar.bz2'.format(meta.dist()),
                               '--user={}'.format(owner)], env=os.environ)
    finally:
        os.remove('token')

if __name__ == '__main__':
    token = os.environ.get('TOKEN')
    owner = 'bioasp'

    cli = get_binstar(argparse.Namespace(token=token, site=None))

    meta = MetaData('.')
    exists = artifact_already_exists(cli, meta, owner)

    if not exists:
        upload(cli, meta, owner)
        print('Uploaded {}'.format(meta.dist()))
    else:
        print('Distribution {} already exists'.format(meta.dist()))
