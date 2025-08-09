#!/usr/bin/env python

from __future__ import annotations
from typing import Iterator, Optional, Union
from rdf.terms import BNode, IRIRef, Literal


class Statement:
    def __init__(self, subject: Union[BNode, IRIRef, Statement],
                 predicate: IRIRef,
                 object: Union[BNode, IRIRef, Literal, Statement],
                 graph_label: Optional[Union[BNode, IRIRef]] = None) -> None:
        """ An RDF Statement; a triple or fact

        :param subject: The subject of the statement.
        :type subject: Union[IRIRef, BNode, Statement]
        :param predicate: The relation between the subject and the object.
        :type predicate: IRIRef
        :param object: The object of the statement
        :type object: Union[IRIRef, BNode, Literal, Statement]
        :param graph_label: An optional label referring to the named graph this
                            statement is a part of.
        :type graph_label: Optional[Union[BNode, IRIRef]]
        :rtype: None
        """
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.graph_label = graph_label

    def __iter__(self) -> Iterator:
        if self.graph_label is None:
            return iter((self.subject,
                         self.predicate,
                         self.object))
        else:
            return iter((self.subject,
                         self.predicate,
                         self.object,
                         self.graph_label))

    def __getitem__(self, index) -> Union[BNode, IRIRef, Literal, Statement]:
        if self.graph_label is None:
            return (self.subject,
                    self.predicate,
                    self.object)[index]
        else:
            return (self.subject,
                    self.predicate,
                    self.object,
                    self.graph_label)[index]

    def __eq__(self, other: object) -> bool:
        """  Return true if self is equal to other.

        Equality is determined by comparing elements pair-wise using standard
        string comparison.

        :param other: [TODO:description]
        :return: [TODO:description]
        """
        if not isinstance(other, Statement):
            return False

        # check all elements pair-wise on equality
        for resourceA, resourceB in ((self.subject, other.subject),
                                     (self.predicate, other.predicate),
                                     (self.object, other.object),
                                     (self.graph_label, other.graph_label)):
            if resourceA != resourceB:
                return False

        return True

    def __lt__(self, other: tuple[object, ...]) -> bool:
        """ Return true if self is less than other.

        Ordering is determined by comparing elements pair-wise using standard
        string comparison order. If the graph label is missing on either of the
        compared statements, only the subject, predicate, and object are
        compaired.

        :param other: [TODO:description]
        :return: [TODO:description]
        """
        return isinstance(other, Statement)\
            and ((self.graph_label is not None
                  and other.graph_label is not None
                  and self.graph_label < other.graph_label)
                 or ((self.graph_label is None
                      or other.graph_label is None
                      or self.graph_label == other.graph_label)
                     and (self.predicate < other.predicate
                          or (type(self.subject) is type(other.subject)
                              and self.subject < other.subject)
                          or (type(self.object) is type(other.object)
                              and self.object < other.object))))

    def __str__(self) -> str:
        out = "%s, %s, %s" % (str(self.subject),
                              str(self.predicate),
                              str(self.object))
        if self.graph_label is not None:
            out += ", %s" % str(self.graph_label)

        return "(" + out + ")"

    def __repr__(self) -> str:
        out = "%s %s %s" % (self.subject,
                            self.predicate,
                            self.object)
        if self.graph_label is not None:
            out += " %s" % self.graph_label

        return out

    def __hash__(self) -> int:
        return hash(repr(self))
