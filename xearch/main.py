#!/usr/bin/python

import os
import sys
import logging
import argparse

import xapian

from cliff.app import App
from cliff.commandmanager import CommandManager

class XearchApp (App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(XearchApp, self).__init__(
            description='full text index and search',
            version='1',
            command_manager=CommandManager('xearch'),
        )

    def initialize_app(self, argv):
        self.log.debug('initialize app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

    def build_option_parser(self, *args, **kwargs):
        parser = super(XearchApp, self).build_option_parser(*args,
                                                            **kwargs)

        parser.add_argument('--documents', '-S',
                            default=os.environ.get('XEARCH_DOCUMENTS',
                                                   '.'))
        parser.add_argument('--database', '--db', '-D',
                            default=os.environ.get('XEARCH_DATABASE'))

        return parser

    def setup_database(self, writable=False):
        if not self.options.database:
            self.options.database = os.path.join(self.options.documents,
                                                 '.xearch')

        dbpath = os.path.join(self.options.documents, self.options.database)
        dbpath = os.path.normpath(dbpath)

        if writable:
            database = xapian.WritableDatabase(dbpath,
                                                xapian.DB_CREATE_OR_OPEN)
        else:
            database = xapian.Database(dbpath)

        self.database_path = dbpath
        self.database = database

def parse_args():
    p = argparse.ArgumentParser()
    return p.parse_args()

def main(argv=sys.argv[1:]):
    myapp = XearchApp()
    return myapp.run(argv)

if __name__ == '__main__':
    sys.exit(main())

