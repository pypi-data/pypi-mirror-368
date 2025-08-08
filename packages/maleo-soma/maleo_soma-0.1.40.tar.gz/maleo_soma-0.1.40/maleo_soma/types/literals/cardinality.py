from typing import Literal, Optional
from maleo_soma.enums.cardinality import Cardinality

type SingleCardinalityLiteral = Literal[Cardinality.SINGLE]

type OptionalSingleCardinalityLiteral = Optional[SingleCardinalityLiteral]

type MultipleCardinalityLiteral = Literal[Cardinality.MULTIPLE]

type OptionalMultipleCardinalityLiteral = Optional[MultipleCardinalityLiteral]

type CardinalityLiteral = Literal[Cardinality.SINGLE, Cardinality.MULTIPLE]

type OptionalCardinalityLiteral = Optional[CardinalityLiteral]
