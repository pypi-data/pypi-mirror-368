# coding:utf-8

from os.path import exists
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

from xkits_logger import Logger

from xpw.configure import Argon2Config
from xpw.configure import BasicConfig
from xpw.configure import DEFAULT_CONFIG_FILE
from xpw.configure import LdapConfig
from xpw.password import Argon2Hasher
from xpw.password import CharacterSet
from xpw.password import Characters  # noqa:H306


class Token():

    def __init__(self, name: str, note: str, hash: str, user: str):  # noqa:E501, pylint:disable=redefined-builtin
        assert isinstance(name, str) and len(name) > 0, f"invalid name: '{name}'"  # noqa:E501
        assert isinstance(note, str) and len(note) > 0, f"invalid note: '{note}'"  # noqa:E501
        assert isinstance(hash, str) and len(hash) > 0, f"invalid hash: '{hash}'"  # noqa:E501
        assert isinstance(user, str) and len(user) > 0, f"illegal user: '{user}'"  # noqa:E501
        self.__name: str = name
        self.__note: str = note
        self.__hash: str = hash
        self.__user: str = user

    def __str__(self) -> str:
        return f"{self.name}, {self.user}, {self.note}"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def note(self) -> str:
        return self.__note

    @property
    def hash(self) -> str:
        return self.__hash

    @property
    def user(self) -> str:
        return self.__user

    def dump(self) -> Tuple[str, str, str]:
        """tuple(note, hash, user)"""
        return (self.note, self.hash, self.user)

    @classmethod
    def spec(cls, note: str, user: str, hash: str = "") -> Tuple[str, str, str, str]:  # noqa:E501, pylint:disable=redefined-builtin
        """tuple(name, note, hash, user)"""
        from uuid import uuid4  # pylint:disable=import-outside-toplevel

        return (str(uuid4()), note, hash or cls.generate(), user)

    @classmethod
    def generate(cls, length: int = 64, characters: Characters = CharacterSet.ALPHANUMERIC) -> str:  # noqa:E501
        """generate a random token"""
        from xpw.password import Pass  # pylint:disable=import-outside-toplevel

        return Pass.random_generate(length=length, characters=characters).value


class ApiToken(Token):
    DEFAULT_USER = "API_DEFAULT_USER"
    DEFAULT_NOTE = "API_TOKEN"

    def __str__(self) -> str:
        return f"{__class__.__name__}({super().__str__()})"

    @classmethod
    def create(cls, user: str = "", note: str = "", hash: str = "") -> "ApiToken":  # noqa:E501, pylint:disable=redefined-builtin
        return cls(*super().spec(note=note or cls.DEFAULT_NOTE, user=user or cls.DEFAULT_USER, hash=hash))  # noqa:E501


class UserToken(Token):

    def __str__(self) -> str:
        return f"{__class__.__name__}({super().__str__()})"

    def renew(self) -> "UserToken":
        return UserToken(name=self.name, note=self.note, hash=self.generate(), user=self.user)  # noqa:E501

    @classmethod
    def create(cls, user: str, note: str) -> "UserToken":
        return cls(*super().spec(note=note, user=user, hash=""))


class TokenAuth():
    TOKEN_SECTION = "tokens"
    API_SECTION = "api"

    def __init__(self, config: BasicConfig):
        config.datas.setdefault(self.TOKEN_SECTION, {})
        config.datas.setdefault(self.API_SECTION, {self.TOKEN_SECTION: {}})
        api_tokens: Dict[str, Tuple[str, str, str]] = config.datas[self.API_SECTION][self.TOKEN_SECTION]  # noqa:E501
        usr_tokens: Dict[str, Tuple[str, str, str]] = config.datas[self.TOKEN_SECTION]  # noqa:E501
        assert isinstance(usr_tokens, dict), f"unexpected type: '{type(usr_tokens)}'"  # noqa:E501
        assert isinstance(api_tokens, dict), f"unexpected type: '{type(api_tokens)}'"  # noqa:E501
        self.__usr_tokens: Dict[str, UserToken] = {v[1]: UserToken(k, *v) for k, v in usr_tokens.items()}  # noqa:E501
        self.__api_tokens: Dict[str, ApiToken] = {v[1]: ApiToken(k, *v) for k, v in api_tokens.items()}  # noqa:E501
        self.__config: BasicConfig = config

    @property
    def config(self) -> BasicConfig:
        return self.__config

    @property
    def user_tokens(self) -> Dict[str, UserToken]:
        """user tokens"""
        return self.__usr_tokens

    @property
    def api_tokens(self) -> Dict[str, ApiToken]:
        """api tokens"""
        return self.__api_tokens

    @property
    def api_options(self) -> Dict[str, Any]:
        return self.config.datas[self.API_SECTION]

    @property
    def api_username(self) -> str:
        return self.api_options.get("user", ApiToken.DEFAULT_USER)

    def create_api_token(self, note: str = "", token: str = "", store: bool = False) -> ApiToken:  # noqa:E501
        """create or random generate random api token"""
        api_token: ApiToken = ApiToken.create(note=note, user=self.api_username, hash=token)  # noqa:E501
        self.api_tokens.setdefault(api_token.hash, api_token)
        if store:
            if token != "":
                raise RuntimeWarning("one-time tokens cannot be stored")
            tokens: Dict[str, Tuple[str, str, str]] = self.api_options[self.TOKEN_SECTION]  # noqa:E501
            tokens[api_token.name] = api_token.dump()
            self.config.dumpf()
        elif token == "":
            Logger.stdout_green(f"Generate one-time api token: {api_token.hash}")  # noqa:E501
        return api_token

    def delete_api_token(self, name: str) -> None:
        tokens: Dict[str, Tuple[str, str, str]] = self.config.datas[self.API_SECTION][self.TOKEN_SECTION]  # noqa:E501
        if token := tokens.get(name):
            del self.api_tokens[token[1]]
            del tokens[name]
            self.config.dumpf()
        else:
            hash: Optional[str] = None  # pylint:disable=redefined-builtin
            for token in self.api_tokens.values():
                if token.name == name:
                    hash = token.hash
                    break
            if isinstance(hash, str):
                del self.api_tokens[hash]
        assert name not in self.config.datas[self.TOKEN_SECTION]

    def verify_api_token(self, hash: str) -> Optional[str]:  # noqa:E501, pylint:disable=W0622
        return token.user if (token := self.api_tokens.get(hash)) else None

    def delete_user_token(self, name: str) -> None:
        tokens: Dict[str, Tuple[str, str, str]] = self.config.datas[self.TOKEN_SECTION]  # noqa:E501
        if token := tokens.get(name):
            del self.user_tokens[token[1]]
            del tokens[name]
            self.config.dumpf()
        assert name not in self.config.datas[self.TOKEN_SECTION]

    def update_user_token(self, name: str) -> Optional[UserToken]:
        tokens: Dict[str, Tuple[str, str, str]] = self.config.datas[self.TOKEN_SECTION]  # noqa:E501
        if token := tokens.get(name):
            old: UserToken = UserToken(name, *token)
            new: UserToken = old.renew()
            assert new.name == name
            del self.user_tokens[old.hash]
            self.user_tokens.setdefault(new.hash, new)
            tokens[name] = new.dump()
            self.config.dumpf()
            return new
        return None

    def verify_user_token(self, hash: str) -> Optional[str]:  # noqa:E501, pylint:disable=W0622
        return token.user if (token := self.user_tokens.get(hash)) else None

    def generate_user_token(self, user: str, note: str) -> UserToken:
        tokens: Dict[str, Tuple[str, str, str]] = self.config.datas[self.TOKEN_SECTION]  # noqa:E501
        tokens.setdefault((token := UserToken.create(user, note)).name, token.dump())  # noqa:E501
        self.user_tokens.setdefault(token.hash, token)
        self.config.dumpf()
        return token

    def verify_token(self, hash: str) -> Optional[str]:  # pylint:disable=W0622
        return self.verify_api_token(hash) or self.verify_user_token(hash)

    def verify_password(self, username: str, password: Optional[str] = None) -> Optional[str]:  # noqa:E501
        raise NotImplementedError()

    def change_password(self, username: str, old_password: str, new_password: str) -> Optional[str]:  # noqa:E501
        """change user password"""
        raise NotImplementedError()

    def create_user(self, username: str, password: str) -> Optional[str]:
        """create new user"""
        raise NotImplementedError()

    def delete_user(self, username: str, password: str) -> bool:
        """delete user"""
        raise NotImplementedError()

    def verify(self, k: str, v: Optional[str] = None) -> Optional[str]:
        if k == "":  # no available username, verify token
            assert isinstance(v, str)
            return self.verify_token(v)

        return self.verify_password(k, v)


class Argon2Auth(TokenAuth):
    def __init__(self, config: BasicConfig):
        super().__init__(Argon2Config(config))

    @property
    def config(self) -> Argon2Config:
        assert isinstance(config := super().config, Argon2Config)
        return config

    def verify_password(self, username: str, password: Optional[str] = None) -> Optional[str]:  # noqa:E501
        try:
            hasher: Argon2Hasher = self.config[username]
            if hasher.verify(password or input("password: ")):
                return username
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return None

    def change_password(self, username: str, old_password: str, new_password: str) -> Optional[str]:  # noqa:E501
        self.config.change(username, old_password, new_password)
        return self.verify_password(username, new_password)

    def create_user(self, username: str, password: str) -> Optional[str]:
        self.config.create(username, password)
        return self.verify_password(username, password)

    def delete_user(self, username: str, password: str) -> bool:
        return self.config.delete(username, password)


class LdapAuth(TokenAuth):
    def __init__(self, config: BasicConfig):
        super().__init__(LdapConfig(config))

    @property
    def config(self) -> LdapConfig:
        assert isinstance(config := super().config, LdapConfig)
        return config

    def verify_password(self, username: str, password: Optional[str] = None) -> Optional[str]:  # noqa:E501
        try:
            config: LdapConfig = self.config
            entry = config.client.signed(config.base_dn, config.filter,
                                         config.attributes, username,
                                         password or input("password: "))
            if entry:
                from ldap3 import Attribute  # pylint:disable=C0415

                name: str = self.config.attributes[0]
                attr: Attribute = getattr(entry, name)
                return str(attr)
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return None

    def change_password(self, username: str, old_password: str, new_password: str) -> Optional[str]:  # noqa:E501
        raise NotImplementedError()

    def create_user(self, username: str, password: str) -> Optional[str]:
        raise NotImplementedError()

    def delete_user(self, username: str, password: str) -> bool:
        raise NotImplementedError()


class AuthInit():  # pylint: disable=too-few-public-methods
    METHODS = {
        Argon2Config.SECTION: Argon2Auth,
        LdapConfig.SECTION: LdapAuth,
    }

    @classmethod
    def from_file(cls, path: str = DEFAULT_CONFIG_FILE) -> TokenAuth:
        config: BasicConfig = BasicConfig.loadf(path) if exists(path) else BasicConfig.new(path)  # noqa:E501
        method: str = config.datas.get("auth_method", Argon2Config.SECTION)
        return cls.METHODS[method](config)
