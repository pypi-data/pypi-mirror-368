from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Absent(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class AbsentOrEqual(_message.Message):
    __slots__ = ["value_to_check"]
    VALUE_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    value_to_check: bytes
    def __init__(self, value_to_check: _Optional[bytes] = ...) -> None: ...

class AbsentOrHashEqual(_message.Message):
    __slots__ = ["hash_to_check"]
    HASH_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    hash_to_check: bytes
    def __init__(self, hash_to_check: _Optional[bytes] = ...) -> None: ...

class AbsentOrNotHashEqual(_message.Message):
    __slots__ = ["hash_to_check"]
    HASH_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    hash_to_check: bytes
    def __init__(self, hash_to_check: _Optional[bytes] = ...) -> None: ...

class Equal(_message.Message):
    __slots__ = ["value_to_check"]
    VALUE_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    value_to_check: bytes
    def __init__(self, value_to_check: _Optional[bytes] = ...) -> None: ...

class NotEqual(_message.Message):
    __slots__ = ["value_to_check"]
    VALUE_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    value_to_check: bytes
    def __init__(self, value_to_check: _Optional[bytes] = ...) -> None: ...

class Present(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PresentAndHashEqual(_message.Message):
    __slots__ = ["hash_to_check"]
    HASH_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    hash_to_check: bytes
    def __init__(self, hash_to_check: _Optional[bytes] = ...) -> None: ...

class PresentAndNotEqual(_message.Message):
    __slots__ = ["value_to_check"]
    VALUE_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    value_to_check: bytes
    def __init__(self, value_to_check: _Optional[bytes] = ...) -> None: ...

class PresentAndNotHashEqual(_message.Message):
    __slots__ = ["hash_to_check"]
    HASH_TO_CHECK_FIELD_NUMBER: _ClassVar[int]
    hash_to_check: bytes
    def __init__(self, hash_to_check: _Optional[bytes] = ...) -> None: ...

class Unconditional(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _Unbounded(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
