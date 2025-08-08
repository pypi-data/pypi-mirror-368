# coding:utf-8

from typing import Iterable
from typing import Optional
from typing import Set


class LdapClient:
    def __init__(self, server, username: str, password: str):
        from ldap3 import Server  # pylint: disable=import-outside-toplevel

        assert isinstance(server, Server), f"{type(server)} is not Server"
        self.__server: Server = server
        self.__bind_dn: str = username
        self.__bind_pw: str = password

    @property
    def server(self):
        return self.__server

    @property
    def bind(self):
        return self.connect(self.server, self.__bind_dn, self.__bind_pw)

    @classmethod
    def connect(cls, server, username: str, password: str):
        from ldap3 import Connection  # pylint: disable=import-outside-toplevel
        from ldap3 import Server  # pylint: disable=import-outside-toplevel

        assert isinstance(server, Server), f"{type(server)} is not Server"
        return Connection(server, username, password, auto_bind=True)

    def search(self, base: str,
               filter: str,  # pylint: disable=redefined-builtin
               attrs: Iterable[str], key: str):
        """search entry"""
        from ldap3 import Attribute  # pylint: disable=import-outside-toplevel
        from ldap3 import Connection  # pylint: disable=import-outside-toplevel
        from ldap3 import Entry  # pylint: disable=import-outside-toplevel

        attributes: Set[str] = set(attrs)
        bind: Connection = self.bind
        bind.search(base, filter, attributes=attributes)
        for entry in bind.entries:
            for attr in attributes:
                attribute: Attribute = getattr(entry, attr)
                if key in attribute.values:
                    assert isinstance(entry, Entry), f"{type(entry)} is not Entry"  # noqa:E501
                    return entry
        return None

    def verify(self, username: str, password: str) -> bool:
        """verify password"""
        try:
            return bool(self.connect(self.server, username, password).bind())
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def signed(self, base: str,  # pylint: disable=R0913,R0917
               filter: str,  # pylint: disable=redefined-builtin
               attrs: Iterable[str], username: str, password: str):
        """search user and verify password"""
        from ldap3 import Entry  # pylint: disable=import-outside-toplevel

        user: Optional[Entry] = self.search(base, filter, attrs, username)
        return user if user and self.verify(user.entry_dn, password) else None


class LdapInit:
    def __init__(self, host: str, port: Optional[int] = None, use_ssl: bool = False):  # noqa:E501
        from ldap3 import ALL  # pylint: disable=import-outside-toplevel
        from ldap3 import Server  # pylint: disable=import-outside-toplevel

        self.__server: Server = Server(host=host, port=port, use_ssl=use_ssl, get_info=ALL)  # noqa:E501

    def bind(self, username: str, password: str) -> LdapClient:
        return LdapClient(self.__server, username, password)

    @classmethod
    def from_url(cls, url: str) -> "LdapInit":
        return cls(host=url)
