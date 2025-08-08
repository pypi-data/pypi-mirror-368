from typing import Literal, Optional
from maleo_soma.enums.secret import SecretFormat

type BytesSecretFormatLiteral = Literal[SecretFormat.BYTES]

type OptionalBytesSecretFormatLiteral = Optional[BytesSecretFormatLiteral]

type StringSecretFormatLiteral = Literal[SecretFormat.STRING]

type OptionalStringSecretFormatLiteral = Optional[StringSecretFormatLiteral]

type SecretFormatLiteral = Literal[SecretFormat.BYTES, SecretFormat.STRING]

type OptionalSecretFormatLiteral = Optional[SecretFormatLiteral]
