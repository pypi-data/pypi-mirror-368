# coding:utf-8

from enum import IntEnum
import string
import sys
from typing import Iterable
from typing import Optional
from typing import Union


class CharacterSet(IntEnum):
    DIGITS = 1
    LOWERCASE = 2
    UPPERCASE = 4
    PUNCTUATION = 8
    LETTERS = LOWERCASE | UPPERCASE
    ALPHANUMERIC = LETTERS | DIGITS
    DEFAULT = DIGITS | LETTERS | PUNCTUATION
    BASIC = LOWERCASE | DIGITS


Characters = Union[str, CharacterSet]  # password characters type


class Secret():
    """Hashed password digest"""

    def __init__(self, key: str):
        self.__key: str = key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return f"Secret({self.key})"

    def __str__(self) -> str:
        return self.key

    def __eq__(self, other: Union["Secret", str]) -> bool:
        return str(other) == self.key if isinstance(other, (Secret, str)) else False  # noqa:E501

    @property
    def key(self) -> str:
        """secret key"""
        return self.__key

    @classmethod
    def generate(cls, length: int = 64, characters: Characters = CharacterSet.DEFAULT) -> "Secret":  # noqa:E501
        """generate a random secret key"""
        return cls(key=Pass.random_generate(length=length, characters=characters).value)  # noqa:E501


class Pass():
    """Password object"""
    SUPERSET = string.digits + string.ascii_letters + string.punctuation
    MIN_LENGTH: int = 4  # minimum password length

    class PasswordError(ValueError):
        def __init__(self, message: str):
            super().__init__(message)

    class MismatchError(PasswordError):
        def __init__(self):
            super().__init__("password mismatch")

    class TooShortError(PasswordError):
        def __init__(self, length: int):
            super().__init__(f"password length {length} must be greater than {Pass.MIN_LENGTH}")  # noqa:E501

    class IllegalCharacterError(PasswordError):
        def __init__(self, char: str):
            super().__init__(f"password contains illegal character: '{char}'")

    class MaxRetriesError(PasswordError):
        def __init__(self, max_retry: int):
            super().__init__(f"reached maximum retries: {max_retry}")

    def __init__(self, value: str):
        self.check(value, throw=True)
        self.__value: str = value

    def __eq__(self, other: Union["Pass", str]) -> bool:
        return self.match(other) if isinstance(other, (Pass, str)) else False

    @property
    def value(self) -> str:
        """password"""
        return self.__value

    @classmethod
    def join(cls, chars: Union[str, Iterable[str]]) -> str:
        """filter out non characters(digits, letters and punctuation)"""
        return "".join([c for c in chars if c in cls.SUPERSET])

    @classmethod
    def check(cls, password: str, throw: bool = False) -> bool:
        """check password is valid"""
        length: int = len(password)
        if length < cls.MIN_LENGTH:
            if throw:
                raise cls.TooShortError(length)
            return False
        for c in password:
            if c not in cls.SUPERSET:
                if throw:
                    raise cls.IllegalCharacterError(c)
                return False
        return True

    def match(self, password: Union["Pass", str], throw: bool = False) -> bool:
        """verify password is match"""
        if isinstance(password, Pass):
            password = password.value
        match: bool = self.value == password
        if throw and not match:
            raise self.MismatchError()
        return match

    @classmethod
    def get_character_set(cls, chars: Characters = CharacterSet.DEFAULT) -> str:  # noqa:E501
        if isinstance(chars, str):
            return cls.join(set(chars))

        characters: str = ""
        if chars & CharacterSet.DIGITS:
            characters += string.digits
        if chars & CharacterSet.LOWERCASE:
            characters += string.ascii_lowercase
        if chars & CharacterSet.UPPERCASE:
            characters += string.ascii_uppercase
        if chars & CharacterSet.PUNCTUATION:
            characters += string.punctuation
        return characters

    @classmethod
    def random_generate(cls, length: Optional[int] = None, characters: Characters = CharacterSet.DEFAULT) -> "Pass":  # noqa:E501
        "generate a random secret key"
        from random import randint  # pylint: disable=import-outside-toplevel

        number: int = max(cls.MIN_LENGTH, length or randint(32, 64))
        chars: str = cls.get_character_set(characters)
        width: int = len(chars)
        password: str = cls.join(chars[randint(1, width) - 1] for _ in range(number))  # noqa:E501
        return cls(password)

    @classmethod
    def dialog(cls, max_retry: int = 3, need_confirm: bool = True) -> "Pass":
        for sn in range(1, min(max(1, max_retry), 10) + 1):
            try:
                from getpass import getpass  # pylint: disable=C0415

                password: Pass = cls(getpass("password: "))
                if need_confirm:  # confirm password is match
                    password.match(getpass("confirm: "), throw=True)
                return password
            except cls.PasswordError as e:
                prompt: str = "please try again" if sn < max_retry else "too many retries"  # noqa:E501
                sys.stderr.write(f"{sn}/{max_retry} {e}, {prompt}\n")
                sys.stderr.flush()
        raise cls.MaxRetriesError(max_retry)


class Salt():
    """Password salt"""
    MIN_LENGTH: int = 8  # minimum length
    DEF_LENGTH: int = 16  # default length

    def __init__(self, value: bytes):
        self.__value: bytes = value.ljust(self.MIN_LENGTH, b"x")

    @property
    def value(self) -> bytes:
        """salt value"""
        return self.__value

    @classmethod
    def format(cls, value: bytes, length: int = DEF_LENGTH) -> "Salt":
        """right-justified password salt"""
        return cls(value.rjust(length, b"x"))

    @classmethod
    def random(cls, length: int = DEF_LENGTH) -> "Salt":
        """generate random password salt"""
        from os import urandom  # pylint: disable=import-outside-toplevel

        return cls(urandom(length))

    @classmethod
    def generate(cls, value: Union[str, bytes, None] = None, length: int = DEF_LENGTH) -> "Salt":  # noqa:E501
        """generate password salt"""
        return cls.random(length) if value is None else cls.format(value.encode("utf-8") if isinstance(value, str) else value)  # noqa:E501


class Argon2Hasher():
    """Argon2 password hasher"""
    DEFAULT_TIME_COST: int = 8
    DEFAULT_MEMORY_COST: int = 65536
    DEFAULT_PARALLELISM: int = 4
    DEFAULT_HASH_LENGTH: int = 32
    DEFAULT_SALT_LENGTH: int = 16

    def __init__(self, hashed: str):
        self.__hashed: str = hashed
        if not isinstance(self.verify(__name__), bool):
            raise ValueError("Invalid hash")
        self.__secret: Secret = Secret(key=hashed.split("$")[-1])

    @property
    def hashed(self) -> str:
        """encoded hash"""
        return self.__hashed

    @property
    def secret(self) -> Secret:
        """secret key"""
        return self.__secret

    def verify(self, password: str) -> bool:
        """verify password is match"""
        from argon2 import PasswordHasher  # pylint: disable=C0415
        from argon2.exceptions import \
            VerifyMismatchError  # pylint: disable=import-outside-toplevel

        try:
            return PasswordHasher().verify(self.hashed, password)
        except VerifyMismatchError:
            return False

    @classmethod
    def hash(cls, password: str,  # pylint: disable=R0913,R0917
             salt: Union[str, bytes, None] = None,
             time_cost: int = DEFAULT_TIME_COST,
             memory_cost: int = DEFAULT_MEMORY_COST,
             parallelism: int = DEFAULT_PARALLELISM,
             hash_len: int = DEFAULT_HASH_LENGTH,
             salt_len: int = DEFAULT_SALT_LENGTH
             ) -> "Argon2Hasher":
        from argon2 import PasswordHasher  # pylint: disable=C0415
        from argon2 import Type  # pylint: disable=import-outside-toplevel

        return cls(hashed=PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
            encoding="utf-8",
            type=Type.ID
        ).hash(password, salt=Salt.generate(salt, salt_len).value))
