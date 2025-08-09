#!/usr/bin/env python

import unittest

from rdf import NTriples
from rdf.graph import Statement
from rdf.terms import IRIRef, Resource


class TestFileParser():
    def testDirect(self):
        i = 0
        g = NTriples(self.PATH)
        for statement in g.parse():
            self.assertIsInstance(statement, Statement)

            s, p, o = statement
            self.assertIsInstance(s, IRIRef)
            self.assertIsInstance(p, IRIRef)
            self.assertIsInstance(o, Resource)

            i += 1

        g.close()

        self.assertEqual(self.NUM_LINES, i)

    def testContext(self):
        i = 0
        with NTriples(self.PATH) as g:
            for statement in g.parse():
                self.assertIsInstance(statement, Statement)

                s, p, o = statement
                self.assertIsInstance(s, IRIRef)
                self.assertIsInstance(p, IRIRef)
                self.assertIsInstance(o, Resource)

                i += 1

        self.assertEqual(self.NUM_LINES, i)


class TestDirectDBpedia(TestFileParser, unittest.TestCase):
    PATH = './tests/dbpedia_sample.nt'
    NUM_LINES = 93


class TestDirectMock(TestFileParser, unittest.TestCase):
    PATH = './tests/mock_sample.nt'
    NUM_LINES = 53


if __name__ == '__main__':
    unittest.main()
