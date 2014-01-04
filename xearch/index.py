#!/usr/bin/python

import os
import sys
import time
import logging
import fnmatch

import xapian
import unicodedata

from cliff.command import Command

class Index(Command):
    log = logging.getLogger(__name__)

    def __init__(self, app, app_args):
        super(Index, self).__init__(app, app_args)
        self.app.setup_database(writable=True)
        self.setup_indexer()

    def get_parser(self, prog_name):
        parser = super(Index, self).get_parser(prog_name)

        parser.add_argument('--exclude', default=[], action='append')
        parser.add_argument('--exclude-from', '-X')

        return parser

    def setup_indexer(self):
        indexer = xapian.TermGenerator()
        stemmer = xapian.Stem('english')
        indexer.set_stemmer(stemmer)

        self.indexer = indexer

    def take_action(self, parsed_args):
        if parsed_args.exclude_from:
            with open(parsed_args.exclude_from) as fd:
                parsed_args.exclude.extend(
                    line.strip() for line in fd
                    if len(line) > 1 and not line.startswith('#'))

        for dirpath, dirnames, filenames in os.walk(
                self.app.options.documents):
            dirnames[:] = [
                name for name in dirnames if not any(
                    fnmatch.fnmatch(name, pattern)
                    for pattern in parsed_args.exclude + ['.xearch'])
            ]

            filenames[:] = [
                name for name in filenames if not any(
                    fnmatch.fnmatch(name, pattern)
                    for pattern in parsed_args.exclude)
            ]

            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                self.add_document(filepath)

        self.app.database.close()

    def add_document(self, filepath):
        self.log.debug('adding %s to index', filepath)
        filestat = os.stat(filepath)
        with open(filepath) as fd:
            data = fd.read()
            try:
                data = unicode(data, 'utf8')
                data = unicodedata.normalize('NFKC', data)
            except UnicodeDecodeError:
                pass

            doc = xapian.Document()
            doc.add_value(0, filepath)
            doc.add_value(1, time.strftime('%Y%m%d',
                                           time.localtime(filestat.st_mtime)))

            indexer = self.indexer
            indexer.set_document(doc)
            filepath_words = ' '.join(filepath.split(os.sep))
            indexer.index_text(filepath_words, 1, 'P')
            indexer.index_text(filepath_words)
            indexer.increase_termpos()
            indexer.index_text(data)

            self.app.database.add_document(doc)

