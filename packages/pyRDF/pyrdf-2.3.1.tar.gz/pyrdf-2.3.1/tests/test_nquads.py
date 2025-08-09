#!/usr/bin/env python

import unittest

from rdf import NQuads
from rdf.graph import Statement
from rdf.terms import IRIRef, Resource


class TestFileParser():
    def testDirect(self):
        i = 0
        g = NQuads(self.PATH)
        for statement in g.parse():
            self.assertIsInstance(statement, Statement)

            s, p, o, l = statement
            self.assertIsInstance(s, IRIRef)
            self.assertIsInstance(p, IRIRef)
            self.assertIsInstance(o, Resource)
            self.assertIsInstance(l, Resource)

            i += 1

        g.close()

        self.assertEqual(self.NUM_LINES, i)

    def testContext(self):
        i = 0
        with NQuads(self.PATH) as g:
            for statement in g.parse():
                self.assertIsInstance(statement, Statement)

                s, p, o, l = statement
                self.assertIsInstance(s, IRIRef)
                self.assertIsInstance(p, IRIRef)
                self.assertIsInstance(o, Resource)
                self.assertIsInstance(l, Resource)

                i += 1

        self.assertEqual(self.NUM_LINES, i)


class TestDirectDBpedia(TestFileParser, unittest.TestCase):
    PATH = './tests/dbpedia_sample.nq'
    NUM_LINES = 93


class TestDirectMock(TestFileParser, unittest.TestCase):
    PATH = './tests/mock_sample.nq'
    NUM_LINES = 53


if __name__ == '__main__':
    unittest.main()
