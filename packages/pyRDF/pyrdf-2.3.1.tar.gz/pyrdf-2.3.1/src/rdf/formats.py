#!/usr/bin/env python

from abc import ABC, abstractmethod
from io import BytesIO, StringIO, TextIOWrapper
import os
from sys import stdout
from typing import Generator, Optional, Self, Tuple, Union
from typing import Literal as Choices

from rdf.graph import Statement
from rdf.terms import Entity, Literal, BNode, IRIRef, Resource


FORMAT_EXTENSION_MAP = {'ntriples': ['.nt', '.nts'], 'nquads': ['.nq', '.nqs']}


class RDF_Serialization_Format(ABC):
    def __init__(self, path: Optional[str] = None,
                 mode: Choices['r', 'w'] = 'r',
                 data: Optional[Union[str, bytes]] = None,
                 encoding: str = 'utf-8',
                 format: Choices["ntriples", "nquads"] = "ntriples") -> None:
        """ General RDF streamer class

        This class is the base class that deals with reading and writung RDF
        data. Normal use is to instantiate one of the subclasses.

        :param path: A path describing the location of an RDF file.
        :type path: Optional[str]
        :param mode: A flag denoting [r]ead or [w]rite mode.
        :type mode: Choices['r', 'w']
        :param data: A valid RDF graph to be read from a string or from
                     standard input.
        :type data: Optional[Union[str,bytes]]
        :param encoding: The file encoding.
        :type encoding: str
        :param format: What serialization format to expect.
        :type format: Choices["ntriples", "nquads"]
        :rtype: None
        """
        self.mode = mode
        self.path = path

        if self.path is None:
            if self.mode == 'r':
                if data is not None:
                    if isinstance(data, str):
                        self._file = StringIO(data)
                    else:  # bytes
                        self._file = TextIOWrapper(BytesIO(data),
                                                   encoding=encoding)
                else:
                    raise Exception("No input source provided")
            elif self.mode == 'w':
                self._file = stdout
            else:
                raise Exception("Unsupported mode: {}".format(self.mode))
        else:
            ext = FORMAT_EXTENSION_MAP[format]
            _, fext = os.path.splitext(self.path)
            if fext not in ext:
                raise Warning(f"Expected one of {ext} but got {fext} instead")

            self._file = open(self.path, self.mode, encoding=encoding)

    def parse(self) -> Generator[Statement, None, None]:
        """ Parse an RDF file and return a generator over its statements.

        :rtype: Generator[Statement, None, None]
        """
        for statement in self._file:
            statement = statement.strip()
            if len(statement) <= 0 or statement.startswith('#'):
                continue

            yield self._parse_statement(statement)

        self._file.seek(0)

    def write(self, statement: Statement) -> None:
        """ Write a single statement.

        :param statement:
        :type statement: Statement
        :rtype: None
        """
        if type(statement) is tuple:
            statement = Statement(*statement)

        self._file.write(self._serialize_statement(statement) + '\n')

    def close(self) -> None:
        """ Close the file.

        :rtype: None
        """
        self._file.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    # Parse functions #####################################

    @abstractmethod
    def _parse_statement(self, statement: str) -> Statement:
        pass

    def _strip_comment(self, statement: str) -> str:
        for i in range(1, len(statement)):
            if statement[-i] == '#':
                break

        return statement[: -i]

    def _parse_subject(self, statement: str)\
            -> Tuple[Union[BNode, IRIRef, Statement], str]:
        if statement.startswith("_:"):
            return self._parse_bnode(statement)
        elif statement.startswith('"<<"'):
            return self._parse_quoted_triple(statement)
        else:  # iriref
            return self._parse_iriref(statement)

    def _parse_predicate(self, statement):
        return self._parse_iriref(statement)

    def _parse_bnode(self, statement: str) -> Tuple[BNode, str]:
        entity, remainder = self._parse_entity(statement)
        bnode = entity.value
        if bnode.startswith('_:'):
            bnode = BNode(bnode[2:])
        else:
            raise Exception("Unexpected format: " + bnode)

        return (bnode, remainder)

    def _parse_graph_label(self, statement: str)\
            -> Tuple[Union[BNode, IRIRef], str]:
        if statement.startswith("_:"):
            return self._parse_bnode(statement)
        else:  # iriref
            return self._parse_iriref(statement)

    def _parse_iriref(self, statement: str) -> Tuple[IRIRef, str]:
        entity, remainder = self._parse_entity(statement)
        iriref = entity.value
        if iriref.startswith('<'):
            iriref = IRIRef(iriref[1:-1])
        else:
            raise Exception("Unexpected format: " + iriref)

        return (iriref, remainder)

    def _parse_entity(self, statement: str) -> Tuple[Entity, str]:
        i = 0
        while i < len(statement) and statement[i] not in [u'\u0009',
                                                          u'\u0020']:
            i += 1

        return (Entity(statement[:i]), statement[i+1:].lstrip())

    def _parse_resource(self, statement: str) -> Tuple[Resource, str]:
        i = 0
        inside_string = False
        while i < len(statement):
            if not inside_string and statement[i] in [u'\u0009', u'\u0020']:
                # check for white space outside of strings
                break

            if statement[i] == '"' and not (i > 0 and statement[i-1] == '\\'):
                # TODO: check if needs escape
                # if we start or end a string
                # account for possible escaped quotation marks
                inside_string = not inside_string

            i += 1

        return (Resource(statement[:i]), statement[i+1:].lstrip())

    def _parse_object(self, statement: str)\
            -> Tuple[Union[BNode, IRIRef, Literal, Statement], str]:
        if statement.startswith('"<<"') and '">>"' in statement:
            # RDF star
            object, remainder = self._parse_quoted_triple(statement)
            return (object, remainder)

        resource, remainder = self._parse_resource(statement)
        resource = resource.value

        if resource.startswith('<'):
            object, _ = self._parse_iriref(resource)
            return (object, remainder)
        if resource.startswith("_:"):
            object, _ = self._parse_bnode(resource)
            return (object, remainder)
        if not resource.startswith('"'):
            raise Exception("Unexpected format: " + resource)

        language = None
        datatype = None
        if resource.endswith('>'):
            # datatype declaration
            for i in range(len(resource)):
                if resource[-i] == '<':
                    break

            datatype = IRIRef(resource[-i+1:-1])
            resource = resource[1:-i-3]  # omit ^^
        elif not resource.endswith('"'):
            # language tag
            for i in range(len(resource)):
                if resource[-i] == '@':
                    break

            language = resource[-i+1:]  # omit @-part
            resource = resource[1:-i-1]
        elif not resource.endswith('"'):
            raise Exception("Unexpected format: " + resource)

        return (Literal(resource, language=language, datatype=datatype),
                remainder)

    def _parse_quoted_triple(self, statement:str) -> Tuple[Statement, str]:
        i = 0
        for j in range(len(statement)):
            # TODO: cope with literals that contain these symbols
            if j < 4:
                continue

            if i <= 0 and statement[j-4:j] == '"<<"':
                i = j  # start position

                continue
            if statement[j-4:j] == '">>"':
                # end position
                break

        quoted_statement = statement[i:j-4].strip()  # omit "<<" and ">>"
        remainder = statement[j:].strip()

        return (self._parse_statement(quoted_statement + ' .'),
                remainder)

    # Serialization functions #####################################

    @abstractmethod
    def _serialize_statement(self, statement: Statement) -> str:
        pass

    def _serialize_quoted_statement(self, statement: Statement) -> str:
        out = '"<<"'
        out += f" {self._serialize_subject(statement.subject)}"
        out += f" {self._serialize_predicate(statement.predicate)}"
        out += f" {self._serialize_object(statement.object)}"
        out += ' ">>"'

        return out

    def _serialize_subject(self, subject: Union[BNode, IRIRef, Statement])\
            -> str:
        if isinstance(subject, Statement):
            return self._serialize_quoted_statement(subject)
        if isinstance(subject, IRIRef):
            return self._serialize_iriref(subject)
        elif isinstance(subject, BNode):
            return self._serialize_bnode(subject)
        else:
            raise Exception("Unrecognised resource: " + subject)

    def _serialize_predicate(self, predicate: IRIRef) -> str:
        return self._serialize_iriref(predicate)

    def _serialize_object(self,
                          object: Union[BNode, IRIRef, Literal, Statement])\
            -> str:
        if isinstance(object, Statement):
            return self._serialize_quoted_statement(object)
        if isinstance(object, IRIRef):
            return self._serialize_iriref(object)
        elif isinstance(object, BNode):
            return self._serialize_bnode(object)
        elif isinstance(object, Literal):
            # literal
            literal = '"' + object.value + '"'
            if object.language is not None:
                literal += '@' + object.language
            elif object.datatype is not None:
                literal += "^^" + self._serialize_iriref(object.datatype)

            return literal
        else:
            raise Exception("Unrecognised resource: " + object)

    def _serialize_graph_label(self, glabel: Optional[Union[BNode, IRIRef]])\
            -> str:
        if isinstance(glabel, IRIRef):
            return self._serialize_iriref(glabel)
        elif isinstance(glabel, BNode):
            return self._serialize_bnode(glabel)
        else:
            raise Exception("Unrecognised resource: " + str(glabel))

    def _serialize_iriref(self, iriref: IRIRef) -> str:
        return '<' + iriref.value + '>'

    def _serialize_bnode(self, bnode: BNode) -> str:
        return '_:' + bnode.value


class NTriples(RDF_Serialization_Format):
    def __init__(self, path: Optional[str] = None, mode: Choices['r', 'w'] = 'r',
                 data: Optional[Union[str, bytes]] = None,
                 encoding: str = 'utf-8') -> None:
        super().__init__(path, mode, data, encoding, format="ntriples")
        """ N-Triples (-Star) parser and serialization class

        :param path: A path describing the location of an RDF file.
        :type path: Optional[str]
        :param mode: A flag denoting [r]ead or [w]rite mode.
        :type mode: Choices['r', 'w']
        :param data: A valid RDF graph to be read from a string or from
                     standard input.
        :type data: Optional[Union[str,bytes]]
        :param encoding: The file encoding.
        :type encoding: str
        :rtype: None
        """

    # Parse functions #####################################

    def _parse_statement(self, statement: str) -> Statement:
        statement = statement.rstrip(' ')
        if not statement.endswith('.'):
            statement = self._strip_comment(statement)
        statement = statement.rstrip(' .')

        subject, remainder = self._parse_subject(statement)
        predicate, remainder = self._parse_predicate(remainder)
        object, _ = self._parse_object(remainder)

        return Statement(subject, predicate, object)

    # Serialization functions #####################################

    def _serialize_statement(self, statement: Statement) -> str:
        subject = self._serialize_subject(statement.subject)
        predicate = self._serialize_predicate(statement.predicate)
        object = self._serialize_object(statement.object)

        return subject + u'\u0020' + predicate + u'\u0020' + object + " ."


class NQuads(RDF_Serialization_Format):
    def __init__(self, path: Optional[str] = None,
                 mode: Choices['r', 'w'] = 'r',
                 data: Optional[Union[str, bytes]] = None,
                 encoding: str = 'utf-8') -> None:
        super().__init__(path, mode, data, encoding, format="nquads")
        """ N-Quads (-Star) parser and serialization class

        :param path: A path describing the location of an RDF file.
        :type path: Optional[str]
        :param mode: A flag denoting [r]ead or [w]rite mode.
        :type mode: Choices['r', 'w']
        :param data: A valid RDF graph to be read from a string or from
                     standard input.
        :type data: Optional[Union[str,bytes]]
        :param encoding: The file encoding.
        :type encoding: str
        :rtype: None
        """

    # Parse functions #####################################

    def _parse_statement(self, statement: str) -> Statement:
        statement = statement.rstrip(' ')
        if not statement.endswith('.'):
            statement = self._strip_comment(statement)
        statement = statement.rstrip(' .')

        subject, remainder = self._parse_subject(statement)
        predicate, remainder = self._parse_predicate(remainder)
        object, remainder = self._parse_object(remainder)

        if len(remainder) > 0:
            graph_label, _ = self._parse_graph_label(remainder)

            return Statement(subject, predicate, object, graph_label)

        # RDF Star
        return Statement(subject, predicate, object)

    # Serialization functions #####################################

    def _serialize_statement(self, statement: Statement) -> str:
        subject = self._serialize_subject(statement.subject)
        predicate = self._serialize_predicate(statement.predicate)
        object = self._serialize_object(statement.object)
        graph_label = self._serialize_graph_label(statement.graph_label)

        return subject + u'\u0020' + predicate + u'\u0020' + object\
            + u'\u0020' + graph_label + " ."
