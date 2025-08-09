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
            try:
                self.assertIsInstance(s, IRIRef)
            except AssertionError:
                self.assertIsInstance(s, Statement)

                self.assertIsInstance(s[0], IRIRef)
                self.assertIsInstance(s[1], IRIRef)
                self.assertIsInstance(s[2], Resource)

            self.assertIsInstance(p, IRIRef)

            try:
                self.assertIsInstance(o, Resource)
            except AssertionError:
                self.assertIsInstance(o, Statement)

                self.assertIsInstance(o[0], IRIRef)
                self.assertIsInstance(o[1], IRIRef)
                self.assertIsInstance(o[2], Resource)

            i += 1

        g.close()

        self.assertEqual(self.NUM_LINES, i)

    def testContext(self):
        i = 0
        with NTriples(self.PATH) as g:
            for statement in g.parse():
                self.assertIsInstance(statement, Statement)

                s, p, o = statement
                try:
                    self.assertIsInstance(s, IRIRef)
                except AssertionError:
                    self.assertIsInstance(s, Statement)

                    self.assertIsInstance(s[0], IRIRef)
                    self.assertIsInstance(s[1], IRIRef)
                    self.assertIsInstance(s[2], Resource)

                self.assertIsInstance(p, IRIRef)

                try:
                    self.assertIsInstance(o, Resource)
                except AssertionError:
                    self.assertIsInstance(o, Statement)

                    self.assertIsInstance(o[0], IRIRef)
                    self.assertIsInstance(o[1], IRIRef)
                    self.assertIsInstance(o[2], Resource)

                i += 1

        self.assertEqual(self.NUM_LINES, i)


class TestDirectMock(TestFileParser, unittest.TestCase):
    PATH = './tests/mock_sample.nt'
    NUM_LINES = 53


if __name__ == '__main__':
    unittest.main()
