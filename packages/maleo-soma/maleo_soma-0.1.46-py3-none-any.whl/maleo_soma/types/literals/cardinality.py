from typing import Literal, Optional
from maleo_soma.enums.cardinality import Cardinality

SingleCardinalityLiteral = Literal[Cardinality.SINGLE]

OptionalSingleCardinalityLiteral = Optional[SingleCardinalityLiteral]

MultipleCardinalityLiteral = Literal[Cardinality.MULTIPLE]

OptionalMultipleCardinalityLiteral = Optional[MultipleCardinalityLiteral]

CardinalityLiteral = Literal[Cardinality.SINGLE, Cardinality.MULTIPLE]

OptionalCardinalityLiteral = Optional[CardinalityLiteral]
