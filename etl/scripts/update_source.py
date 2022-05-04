# -*- coding: utf-8 -*-

import os
import sys
import argparse
import tempfile
import shutil
from ddf_utils.factory import ihme
from queries import QUERIES, VERSION, EMAIL

source_dir = '../source'

taskIDs = {
    'deaths_number_rate': '42952e589a846e6f9bc825c73d56f99f'
}

m = ihme.IHMELoader()


def remove_old_source():
    full_path = os.path.abspath(source_dir)
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
    os.makedirs(full_path)


def run_query(q, ver):
    q_id = q.pop('id')
    print('running query: {}'.format(q_id))
    context = q.pop('context')
    m.send_query(ver, context, **q)


def run_download(context, taskID):
    out_dir = os.path.join(source_dir, context)
    os.makedirs(out_dir, exist_ok=True)
    print(f'downloading task {taskID} into {out_dir}')
    m.bulk_download(out_dir, taskID)


def main(force_update=False):
    md = m.load_metadata()
    version = md['version'].sort_values(by='id').iloc[-1, 0]
    print('latest version is: {}'.format(version))
    print('query version is {}'.format(VERSION))

    if force_update:
        if version == VERSION:
            print('downloading files...')
            remove_old_source()
            for k, v in taskIDs.items():
                run_download(k, v)
            print('all done.')
        else:
            print('new version detected!  I will send query to the GBD tool'
                  'please check your email and update the taskID list variable.'
                  'and re-run the script')
            print(f'email address: {EMAIL}')
            for q in QUERIES:
                run_query(q, version)
    else:
        if version == VERSION:
            print('no new version, keep using old source files.')
        else:
            print('new version detected!  Please run the script again manually with --force')
            raise ValueError('new version detected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', help='force update',
                        action=argparse.BooleanOptionalAction)
    args = vars(parser.parse_args(sys.argv[1:]))
    if args['force']:
        main(force_update=True)
    else:
        main(force_update=False)
