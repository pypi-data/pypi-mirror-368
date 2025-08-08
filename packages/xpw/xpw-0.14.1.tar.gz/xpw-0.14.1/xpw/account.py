# coding:utf-8

from os import makedirs
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import isdir
from os.path import join
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from xkits_lib.cache import CacheItem
from xkits_lib.unit import TimeUnit

from xpw.authorize import ApiToken
from xpw.authorize import AuthInit
from xpw.authorize import Token as BaseToken
from xpw.authorize import TokenAuth
from xpw.authorize import UserToken
from xpw.configure import DEFAULT_CONFIG_FILE
from xpw.session import SessionID
from xpw.session import SessionKeys
from xpw.session import SessionUser


class Profile():
    class Token():
        def __init__(self, token: BaseToken):
            self.__token: BaseToken = token

        @property
        def name(self) -> str:
            return self.__token.name

        @property
        def note(self) -> str:
            return self.__token.note

    class Session():  # pylint:disable=too-few-public-methods
        def __init__(self, item: CacheItem[str, SessionUser]):
            self.__item: CacheItem[str, SessionUser] = item

        @property
        def session_id(self) -> str:
            return super(CacheItem, self.__item).data.session_id

        @property
        def expired(self) -> bool:
            return self.__item.expired

    def __init__(self, accounts: "Account", username: str):  # noqa:E501
        self.__accounts: Account = accounts  # private
        self.__username: str = username

    @property
    def catalog(self) -> str:
        return self.__accounts.catalog

    @property
    def username(self) -> str:
        return self.__username

    @property
    def identity(self) -> str:
        return self.username

    @property
    def workspace(self) -> str:
        return join(self.catalog, self.username)

    @property
    def administrator(self) -> bool:
        return self.username in self.__accounts.administrators

    @property
    def tokens(self) -> Iterator[Token]:
        for token in self.__accounts.members.user_tokens.values():
            if token.user == self.username:
                yield self.Token(token)

    @property
    def api_tokens(self) -> Iterator[Token]:
        if not self.administrator:
            raise PermissionError("administrator privileges are required")

        for token in self.__accounts.members.api_tokens.values():
            yield self.Token(token)

    @property
    def sessions(self) -> Iterator[Session]:
        for session_id in self.__accounts.tickets.logged.get(self.username, []):  # noqa:E501
            yield self.Session(self.__accounts.tickets[session_id])

    def logout(self) -> bool:
        self.__accounts.tickets.quit(self.username)
        return not any(self.sessions)

    def create_api_token(self, note: str, store: bool = True) -> ApiToken:
        if not self.administrator:
            raise PermissionError("administrator privileges are required")

        return self.__accounts.members.create_api_token(note=note, store=store)

    def delete_api_token(self, token: str) -> bool:
        if not self.administrator:
            raise PermissionError("administrator privileges are required")

        found: bool = False
        for item in self.api_tokens:
            if item.name == token:
                found = True
                break

        if found:
            self.__accounts.members.delete_api_token(name=token)

        for item in self.api_tokens:
            if item.name == token:
                return False  # pragma: no cover
        return True

    def create_token(self, note: str) -> UserToken:
        return self.__accounts.members.generate_user_token(user=self.username, note=note)  # noqa:E501

    def update_token(self, token: str) -> Optional[UserToken]:
        found: bool = False
        for item in self.tokens:
            if item.name == token:
                found = True
                break
        return self.__accounts.members.update_user_token(name=token) if found else None  # noqa:E501

    def delete_token(self, token: str) -> bool:
        found: bool = False
        for item in self.tokens:
            if item.name == token:
                found = True
                break

        if found:
            self.__accounts.members.delete_user_token(name=token)

        for item in self.tokens:
            if item.name == token:
                return False  # pragma: no cover
        return True


class Account():  # pylint:disable=too-many-public-methods
    ACCOUNT_SECTION = "account"
    ADMIN_SECTION = "admin"

    def __init__(self, auth: TokenAuth, lifetime: Optional[TimeUnit] = 2592000,
                 secret_key: Optional[str] = None):  # expires in 30 days
        if lifetime is None:
            lifetime = auth.config.lifetime

        base: str = abspath(auth.config.datas.get("workspace", dirname(auth.config.path)))  # noqa:E501
        keys: SessionKeys = SessionKeys(secret_key or auth.config.secret_key, lifetime)  # noqa:E501

        auth.config.datas.setdefault(self.ADMIN_SECTION, {"user": ""})
        section: Dict[str, Any] = auth.config.datas[self.ADMIN_SECTION]
        if isinstance(admin := section["user"], str):
            section["user"] = [user for item in admin.split(",") if (user := item.strip())]  # noqa:E501
        assert isinstance(section["user"], list)

        if not exists(base):
            makedirs(base)  # pragma: no cover
        assert isdir(base)

        self.__tickets: SessionKeys = keys
        self.__members: TokenAuth = auth
        self.__catalog: str = base

    @property
    def tickets(self) -> SessionKeys:
        return self.__tickets

    @property
    def members(self) -> TokenAuth:
        return self.__members

    @property
    def catalog(self) -> str:
        return self.__catalog

    @property
    def options(self) -> Dict[str, Any]:
        return self.members.config.datas.get(self.ACCOUNT_SECTION, {})

    @property
    def allow_register(self) -> bool:
        return bool(self.options.get("register"))

    @property
    def allow_terminate(self) -> bool:
        return bool(self.options.get("terminate"))

    @property
    def admin_options(self) -> Dict[str, Any]:
        return self.members.config.datas.get(self.ADMIN_SECTION, {})

    @property
    def administrators(self) -> List[str]:
        return self.admin_options["user"]

    @property
    def first_user_is_admin(self) -> bool:
        return bool(self.admin_options.get("first_auto"))

    @property
    def allow_admin_create_user(self) -> bool:
        return bool(self.admin_options.get("create_user"))

    @property
    def allow_admin_delete_user(self) -> bool:
        return bool(self.admin_options.get("delete_user"))

    def fetch(self, session_id: str, secret_key: Optional[str] = None) -> Optional[Profile]:  # noqa:E501
        """generate profile for authenticated user"""
        return Profile(self, identity) if (identity := self.tickets.lookup(session_id, secret_key)) is not None else None  # noqa:E501

    def check(self, session_id: str, secret_key: Optional[str] = None) -> bool:
        return self.tickets.verify(session_id, secret_key)

    def login(self, username: str, password: str,
              session_id: Optional[str] = None,
              secret_key: Optional[str] = None
              ) -> Optional[SessionUser]:
        identity: Optional[str] = self.members.verify(username, password)

        if not isinstance(identity, str):
            return None

        if username == "":  # token login request
            if identity == self.members.api_username:  # api without session
                return SessionUser(session_id=session_id or "", secret_key=self.tickets.secret.key, identity=identity)  # noqa:E501
            if identity == "":  # token not bound user
                return None  # pragma: no cover
            username = identity

        if username != identity:
            return None  # pragma: no cover

        _session_id = session_id or SessionID.generate()
        self.tickets.sign_in(_session_id, secret_key, username)
        return self.tickets.get(_session_id).data

    def logout(self, session_id: str, secret_key: Optional[str] = None) -> bool:  # noqa:E501
        return profile.logout() if (profile := self.fetch(session_id, secret_key)) else False  # noqa:E501

    def register(self, username: str, password: str) -> Optional[Profile]:
        if not self.allow_register:
            raise PermissionError("register new account is disabled")

        import string  # pylint:disable=import-outside-toplevel

        allowed_characters = string.ascii_letters + string.digits + "_"
        if not username or any(c not in allowed_characters for c in username):
            raise ValueError(f"register an illegal username: '{username}'")

        user: Optional[str] = self.members.create_user(username, password)
        if self.first_user_is_admin and user and len(self.administrators) == 0:
            self.administrators.append(user)
            self.members.config.dumpf()
        return Profile(self, user) if user else None

    def terminate(self, username: str, password: str) -> bool:
        if not self.allow_terminate:
            raise PermissionError("terminate account is disabled")

        if len(self.administrators) <= 1 and username in self.administrators:
            raise PermissionError(f"administrator '{username}' cannot be terminated")  # noqa:E501

        # step 1: force verify username/password and logout accout
        if self.members.verify_password(username, password) == username and (profile := Profile(self, username)).logout():  # noqa:E501
            # step 2: delete all tokens associated with the user
            for name in [token.name for token in profile.tokens]:  # noqa:E501
                self.members.delete_user_token(name)
            # step 3: delete the user account
            return self.members.delete_user(username, password)
        return False

    def create_token(self, session_id: str, secret_key: Optional[str] = None, note: str = "") -> Optional[UserToken]:  # noqa:E501
        """generate random token for authenticated user"""
        return profile.create_token(note or f"{profile.identity}_token".upper()) if (profile := self.fetch(session_id, secret_key)) else None  # noqa:E501

    def update_token(self, session_id: str, secret_key: Optional[str] = None, token: str = "") -> Optional[UserToken]:  # noqa:E501
        """update token for authenticated user"""
        return profile.update_token(token) if (profile := self.fetch(session_id, secret_key)) else None  # noqa:E501

    def delete_token(self, session_id: str, secret_key: Optional[str] = None, token: str = "") -> bool:  # noqa:E501
        """delete token for authenticated user"""
        return profile.delete_token(token) if (profile := self.fetch(session_id, secret_key)) else False  # noqa:E501

    @classmethod
    def from_file(cls, config: str = DEFAULT_CONFIG_FILE,
                  lifetime: Optional[TimeUnit] = None,
                  secret_key: Optional[str] = None) -> "Account":
        auth: TokenAuth = AuthInit.from_file(path=abspath(config))
        return cls(auth=auth, lifetime=lifetime, secret_key=secret_key)


if __name__ == "__main__":
    Account.from_file().members.config.dumpf()
