from typing import Literal, Optional
from maleo_soma.enums.key import KeyFormat, RSAKeyType

type BytesKeyFormatLiteral = Literal[KeyFormat.BYTES]

type OptionalBytesKeyFormatLiteral = Optional[BytesKeyFormatLiteral]

type StringKeyFormatLiteral = Literal[KeyFormat.STRING]

type OptionalStringKeyFormatLiteral = Optional[StringKeyFormatLiteral]

type KeyFormatLiteral = Literal[KeyFormat.BYTES, KeyFormat.STRING]

type OptionalKeyFormatLiteral = Optional[KeyFormatLiteral]

type PrivateRSAKeyTypeLiteral = Literal[RSAKeyType.PRIVATE]

type OptionalPrivateRSAKeyTypeLiteral = Optional[PrivateRSAKeyTypeLiteral]

type PublicRSAKeyTypeLiteral = Literal[RSAKeyType.PUBLIC]

type OptionalPublicRSAKeyTypeLiteral = Optional[PublicRSAKeyTypeLiteral]

type RSAKeyTypeLiteral = Literal[RSAKeyType.PRIVATE, RSAKeyType.PUBLIC]

type OptionalRSAKeyTypeLiteral = Optional[RSAKeyTypeLiteral]
