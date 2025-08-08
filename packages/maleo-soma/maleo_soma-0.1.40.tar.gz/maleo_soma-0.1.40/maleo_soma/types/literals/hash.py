from typing import Literal, Optional
from maleo_soma.enums.hash import Mode

type ObjectModeLiteral = Literal[Mode.OBJECT]

type OptionalObjectModeLiteral = Optional[ObjectModeLiteral]

type DigestModeLiteral = Literal[Mode.DIGEST]

type OptionalDigestModeLiteral = Optional[DigestModeLiteral]

type ModeLiteral = Literal[Mode.OBJECT, Mode.DIGEST]

type OptionalModeLiteral = Optional[ModeLiteral]
