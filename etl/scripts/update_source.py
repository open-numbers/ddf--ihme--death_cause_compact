# -*- coding: utf-8 -*-

import os
import tempfile
import shutil
from ddf_utils.factory import ihme

from queries import QUERIES, VERSION

source_dir = '../source'

m = ihme.IHMELoader()


def remove_old_source():
    full_path = os.path.abspath(source_dir)
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
    os.makedirs(full_path)


def run_query(q):
    q_id = q.pop('id')
    print('running query: {}'.format(q_id))
    context = [q.pop('context')]

    tmp_dir = tempfile.mkdtemp()
    folders = m.bulk_download(tmp_dir, VERSION, context, **q)

    if not folders:
        print('download was not completed.')
        raise ValueError('downloader failed')

    # there should be one folder
    assert len(folders) == 1

    out_dir = os.path.join(source_dir, q_id)
    os.makedirs(out_dir, exist_ok=True)

    folder = os.path.join(tmp_dir, folders[0])
    for f in os.listdir(folder):
        if f.startswith('IHME') and f.endswith('zip'):
            shutil.move(os.path.join(folder, f), out_dir)
    print('downloaded.')


def main():
    md = m.load_metadata()
    version = md['version'].sort_values(by='id').iloc[-1, 0]
    print('latest version is: {}'.format(version))
    print('query version is {}'.format(VERSION))

    remove_old_source()

    for q in QUERIES:
        run_query(q)

    print('all done.')


if __name__ == '__main__':
    main()
