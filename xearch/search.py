#!/usr/bin/python

import os
import sys
import logging
import xapian

from cliff.command import Command

class Search(Command):
    log = logging.getLogger(__name__)

    def __init__(self, app, app_args):
        super(Search, self).__init__(app, app_args)
        self.app.setup_database()
        self.setup_queryparser()

    def setup_queryparser(self):
        qp = xapian.QueryParser()
        stemmer = xapian.Stem('english')
        qp.set_stemmer(stemmer)
        qp.add_valuerangeprocessor(
            xapian.DateValueRangeProcessor(1, 'date:', True, False, 1900)
        )
        qp.add_prefix('path', 'S')

        self.queryparser = qp

    def get_parser(self, prog_name):
        parser = super(Search, self).get_parser(prog_name)
        parser.add_argument('--offset', '-O', default=0, type=int)
        parser.add_argument('--pagesize', '-P', default=100, type=int)
        parser.add_argument('query', nargs='+')
        return parser

    def take_action(self, parsed_args):
        query = self.queryparser.parse_query(' '.join(parsed_args.query))
        enquire = xapian.Enquire(self.app.database)
        enquire.set_query(query)
        enquire.set_collapse_key(0)

        for match in enquire.get_mset(parsed_args.offset,
                                      parsed_args.pagesize,
                                      100):
            print match.document.get_value(0)

