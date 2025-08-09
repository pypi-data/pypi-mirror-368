#!/usr/bin/env python


from __future__ import annotations
from typing import Any, Optional


class Resource:
    def __init__(self, value: str) -> None:
        """ An RDF Resource.

        :param value: The value corresponding to this resource.
        :type value: str
        :rtype: None
        """
        self.value = value

    def __eq__(self, other) -> bool:
        return type(self) is type(other)\
                and self.value == other.value

    def __lt__(self, other: Resource) -> bool:
        return type(self) is type(other)\
                and self.value < other.value

    def __len__(self) -> int:
        return len(self.value)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(repr(self))


class Entity(Resource):
    def __init__(self, value: str):
        """ An Entity; a thing, tangible or otherwise.

        :param value: The identifier of the entity.
        :type value: str
        """
        super().__init__(value)


class BNode(Entity):
    def __init__(self, value: str) -> None:
        """ A Blank Node

        :param value: The identifier of the entity.
        :type value: str
        :rtype: None
        """
        super().__init__(value)


class IRIRef(Entity):
    def __init__(self, value: str) -> None:
        """ An RDF URI or IRI.

        :param value: The identifier of the entity.
        :type value: str
        :rtype: None
        """
        super().__init__(value)

    def __add__(self, other: Any) -> IRIRef:
        return IRIRef(self.value + str(other))


class Literal(Resource):
    def __init__(self, value: str, datatype: Optional[IRIRef] = None,
                 language: Optional[str] = None) -> None:
        """ An RDF Literal.

        :param value: The value of the literal.
        :type value: str
        :param datatype: An optional datatype.
        :type datatype: Optional[IRIRef]
        :param language: An optional language tag
        :type language: Optional[str]
        :rtype: None
        """
        super().__init__(value)

        if datatype is not None and language is not None:
            raise Warning("Accepts either datatype or language, not both")

        self.datatype = datatype
        self.language = language

    def __eq__(self, other: Literal) -> bool:
        return type(other) is Literal\
                and self.value == other.value\
                and self.datatype == other.datatype\
                and self.language == other.language

    def __hash__(self) -> int:
        value = str()
        if self.datatype is not None:
            value = self.datatype
        if self.language is not None:
            value = self.language

        return hash(repr(self)+repr(value))
