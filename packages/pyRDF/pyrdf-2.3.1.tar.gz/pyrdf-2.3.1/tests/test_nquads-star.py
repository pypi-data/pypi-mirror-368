#!/usr/bin/env python

import unittest

from rdf import NQuads
from rdf.graph import Statement
from rdf.terms import BNode, IRIRef, Resource


class TestFileParser():
    def testDirect(self):
        i = 0
        g = NQuads(self.PATH)
        for statement in g.parse():
            self.assertIsInstance(statement, Statement)

            s, p, o, l = statement
            try:
                self.assertIsInstance(s, IRIRef)
            except AssertionError:
                try:
                    self.assertIsInstance(s, BNode)
                except AssertionError:
                    self.assertIsInstance(s, Statement)

                    self.assertIsInstance(s.subject, IRIRef)
                    self.assertIsInstance(s.predicate, IRIRef)
                    self.assertIsInstance(s.object, Resource)

            self.assertIsInstance(p, IRIRef)

            try:
                self.assertIsInstance(o, Resource)
            except AssertionError:
                self.assertIsInstance(o, Statement)

                self.assertIsInstance(o.subject, IRIRef)
                self.assertIsInstance(o.predicate, IRIRef)
                self.assertIsInstance(o.object, Resource)

            try:
                self.assertIsInstance(l, IRIRef)
            except AssertionError:
                self.assertIsInstance(l, BNode)

            i += 1

        g.close()

        self.assertEqual(self.NUM_LINES, i)

    def testContext(self):
        i = 0
        with NQuads(self.PATH) as g:
            for statement in g.parse():
                self.assertIsInstance(statement, Statement)

                s, p, o, l = statement
                try:
                    self.assertIsInstance(s, IRIRef)
                except AssertionError:
                    try:
                        self.assertIsInstance(s, BNode)
                    except AssertionError:
                        self.assertIsInstance(s, Statement)

                        self.assertIsInstance(s.subject, IRIRef)
                        self.assertIsInstance(s.predicate, IRIRef)
                        self.assertIsInstance(s.object, Resource)

                self.assertIsInstance(p, IRIRef)

                try:
                    self.assertIsInstance(o, Resource)
                except AssertionError:
                    self.assertIsInstance(o, Statement)

                    self.assertIsInstance(o.subject, IRIRef)
                    self.assertIsInstance(o.predicate, IRIRef)
                    self.assertIsInstance(o.object, Resource)

                try:
                    self.assertIsInstance(l, IRIRef)
                except AssertionError:
                    self.assertIsInstance(l, BNode)

                i += 1

        self.assertEqual(self.NUM_LINES, i)


class TestDirectMock(TestFileParser, unittest.TestCase):
    PATH = './tests/mock_sample.nqs'
    NUM_LINES = 55


if __name__ == '__main__':
    unittest.main()
