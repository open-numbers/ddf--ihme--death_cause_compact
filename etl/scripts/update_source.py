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
    'deaths_number_rate': '4f4ce6aef1cba0568dacadb727a22b08',
    'incidence_number_rate': '15571ecd990ca9fd7ea01a3a9d223d7b'
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


def main(action=None):
    md = m.load_metadata()
    version = md['version'].sort_values(by='id').iloc[-1, 0]
    print('latest version is: {}'.format(version))
    print('query version is {}'.format(VERSION))

    if action == 'download':
        if version != VERSION:
            print('WARNING: new version detected.')
        print('downloading files...')
        remove_old_source()
        for k, v in taskIDs.items():
            run_download(k, v)
        print('all done.')
    elif action == 'query':
        print('GBD Result tool now require register and login')
        print('Can not do it via script right now...')
        raise NotImplementedError('can not send query')
        # print(f'email address: {EMAIL}')
        # for q in QUERIES:
        #     run_query(q, version)
    else:
        # TODO: how to make airflow server reuse old source files?
        if version == VERSION:
            print('no new version, keep using old source files.')
        else:
            print('new version detected!  Please run the script again manually with --query')
            raise ValueError('new version detected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', help='send query', action='store_true')
    parser.add_argument('--download', help='download all tasks', action='store_true')
    args = vars(parser.parse_args(sys.argv[1:]))
    if args['query'] and args['download']:
        raise ValueError('--query and --download can not be set at same time')
    if args['query']:
        main(action='query')
    elif args['download']:
        main(action='download')
    else:
        main(action=None)
