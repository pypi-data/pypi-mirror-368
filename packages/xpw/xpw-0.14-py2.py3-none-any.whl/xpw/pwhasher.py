# coding:utf-8

from errno import EINVAL
from typing import Optional
from typing import Sequence

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from xpw.attribute import __urlhome__
from xpw.attribute import __version__
from xpw.password import Argon2Hasher
from xpw.password import Pass

DEFAULT_FILE = "xpwhashed"


def get_password(password: Optional[str], dialog_confirm: bool) -> Pass:
    return Pass.dialog(need_confirm=dialog_confirm) if password is None else Pass(password)  # noqa:E501


@CommandArgument("verify", description="verify password")
def add_cmd_verify(_arg: ArgParser):
    _arg.add_argument("--hash", dest="password_hash", metavar="FILE", default=DEFAULT_FILE,  # noqa:E501
                      help=f"encoded hash file, default is '{DEFAULT_FILE}'")
    _arg.add_argument(dest="password", metavar="TEXT", nargs="?",
                      help="password plaintext, default secure input via dialog")  # noqa:E501


@CommandExecutor(add_cmd_verify)
def run_cmd_verify(cmds: Command) -> int:
    password: Pass = get_password(cmds.args.password, dialog_confirm=False)
    password_hash: str = cmds.args.password_hash
    with open(password_hash, "r", encoding="utf-8") as rhdl:
        hashed: str = rhdl.read().strip()
    if not Argon2Hasher(hashed).verify(password.value):
        cmds.stderr_red("password mismatch")
        return EINVAL
    cmds.stdout_green("password match")
    return 0


@CommandArgument("encode", description="compute encoded hash")
def add_cmd_encode(_arg: ArgParser):
    _arg.add_argument("--store", dest="password_hash", metavar="FILE", nargs="?", const=DEFAULT_FILE,  # noqa:E501
                      help=f"store encoded hash to file, default is '{DEFAULT_FILE}'")  # noqa:E501
    _arg.add_argument("--password", dest="password", metavar="TEXT",
                      help="password plaintext, default secure input via dialog")  # noqa:E501
    _arg.add_argument(dest="password_salt", metavar="SALT", nargs="?",
                      help="password salt, default is random value")


@CommandExecutor(add_cmd_encode)
def run_cmd_encode(cmds: Command) -> int:
    password: Pass = get_password(cmds.args.password, dialog_confirm=True)
    password_salt: Optional[str] = cmds.args.password_salt
    password_hash: Optional[str] = cmds.args.password_hash
    hasher: Argon2Hasher = Argon2Hasher.hash(
        password=password.value, salt=password_salt,
        time_cost=16, memory_cost=65536, parallelism=8,
        hash_len=64, salt_len=32)
    if isinstance(password_hash, str):
        with open(password_hash, "w", encoding="utf-8") as whdl:
            cmds.stdout(f"store encoded hash to file: {password_hash}")
            whdl.write(hasher.hashed)
    else:
        cmds.stdout(hasher.hashed)
    return 0


@CommandArgument("pwhasher", description="compute encoded hash or verify password")
def add_cmd(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd, add_cmd_encode, add_cmd_verify)
def run_cmd(cmds: Command) -> int:  # pylint: disable=unused-argument
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
