# coding:utf-8

from typing import Dict
from typing import List
from typing import Optional

from xkits_lib.cache import CacheExpired
from xkits_lib.cache import CacheItem
from xkits_lib.cache import CacheMiss
from xkits_lib.cache import ItemPool
from xkits_lib.unit import TimeUnit

from xpw.password import Pass
from xpw.password import Secret


class SessionID():
    def __init__(self, user_agent: str, session_id: Optional[str] = None):
        self.__session_id: str = session_id or self.generate()
        self.__user_agent: str = user_agent

    @property
    def number(self) -> str:
        return self.__session_id

    @property
    def detail(self) -> str:
        return self.__user_agent

    @property
    def digest(self) -> str:
        return self.encode(self.detail)

    def verify(self, user_agent) -> bool:
        return self.digest == self.encode(user_agent)

    @classmethod
    def encode(cls, user_agent: str) -> str:
        from hashlib import md5  # pylint: disable=import-outside-toplevel

        return md5(user_agent.encode("utf-8")).hexdigest()

    @classmethod
    def generate(cls) -> str:
        """Generate a 32-bit hexadecimal random session_id"""
        return Pass.random_generate(32, "0123456789abcdef").value


class SessionUser():
    def __init__(self, session_id: str, secret_key: str, identity: str = ""):  # noqa:E501
        self.__session_id: str = session_id
        self.__secret_key: str = secret_key
        self.__identity: str = identity

    def __str__(self) -> str:
        return f"{__class__.__name__}(session_id={self.__session_id}, identity={self.__identity})"  # noqa:E501

    @property
    def session_id(self) -> str:
        return self.__session_id

    @property
    def secret_key(self) -> str:
        return self.__secret_key

    @property
    def identity(self) -> str:
        return self.__identity

    def update(self, secret_key: str, identity: str = "") -> None:
        self.__secret_key = secret_key
        self.__identity = identity

    def verify(self, session_id: str, secret_key: str) -> bool:
        return self.session_id == session_id and self.secret_key == secret_key


class SessionKeys(ItemPool[str, SessionUser]):
    """Session Secret Pool"""

    def __init__(self, secret_key: Optional[str] = None, lifetime: TimeUnit = 3600.0):  # noqa:E501
        self.__secret: Secret = Secret(secret_key or Pass.random_generate(64).value)  # noqa:E501
        self.__logged: Dict[str, List[str]] = {}
        super().__init__(lifetime=lifetime)

    @property
    def logged(self) -> Dict[str, List[str]]:
        return self.__logged

    @property
    def secret(self) -> Secret:
        return self.__secret

    def search(self, s: Optional[str] = None) -> CacheItem[str, SessionUser]:
        session_id: str = s or SessionID.generate()
        if session_id not in self:
            self.put(session_id, SessionUser(session_id, self.secret.key))
        return self.get(session_id)

    def lookup(self, session_id: str, secret_key: Optional[str] = None) -> Optional[str]:  # noqa:E501
        try:
            item: CacheItem[str, SessionUser] = self[session_id]
            user: SessionUser = item.data
            if user.verify(session_id, secret_key or self.secret.key):
                item.renew()
                return user.identity
            return None
        except (CacheExpired, CacheMiss):
            return None

    def verify(self, session_id: str, secret_key: Optional[str] = None) -> bool:  # noqa:E501
        try:
            item: CacheItem[str, SessionUser] = self[session_id]
            user: SessionUser = super(CacheItem, item).data

            if not secret_key:
                secret_key = self.secret.key

            if not user.verify(session_id, secret_key):
                return False

            for _session_id in self.logged.get(user.identity, []):
                if not self[_session_id].expired:
                    item.renew()  # only renew oneself
                    return True

            return False  # all sessions expired, pragma: no cover
        except CacheMiss:
            return False

    def sign_in(self, session_id: str, secret_key: Optional[str] = None, identity: str = "") -> str:  # noqa:E501
        item: CacheItem[str, SessionUser] = self.search(session_id)
        item.renew()  # ignore CacheExpired exception during login
        (user := item.data).update(secret_key or self.secret.key, identity)
        if user.session_id not in (logged := self.logged.setdefault(user.identity, [])):  # noqa:E501
            logged.append(user.session_id)
        assert session_id in self.logged[identity]
        return user.secret_key

    def sign_out(self, session_id: str) -> None:
        item: CacheItem[str, SessionUser] = self.get(session_id)
        user: SessionUser = super(CacheItem, item).data
        return self.quit(user.identity)

    def quit(self, identity: str) -> None:
        for session_id in self.logged[identity]:
            self.delete(session_id)
        del self.logged[identity]
