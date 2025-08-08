# coding:utf-8

import string
from typing import Optional
from typing import Sequence

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from xpw.attribute import __urlhome__
from xpw.attribute import __version__
from xpw.password import Pass

DEFAULT_CHARACTERS = string.digits + string.ascii_lowercase


@CommandArgument("randkey", description="generate a random secret key")
def add_cmd(_arg: ArgParser):
    _arg.add_argument("--characters", dest="characters", type=str,
                      metavar="CHAR", default=DEFAULT_CHARACTERS,
                      help="secret key contains specify characters")
    _arg.add_opt_on("--enable-digit", dest="enable_digit",
                    help="secret key contains digit")
    _grp = _arg.add_mutually_exclusive_group()
    _grp.add_argument("--enable-letter", dest="enable_letter", action="store_true",  # noqa:E501
                      help="secret key contains ascii letter")
    _grp.add_argument("--enable-lowercase", dest="enable_lowercase", action="store_true",  # noqa:E501
                      help="secret key contains lowercase letter")
    _grp.add_argument("--enable-uppercase", dest="enable_uppercase", action="store_true",  # noqa:E501
                      help="secret key contains uppercase letter")
    _arg.add_opt_on("--enable-punctuation", dest="enable_punctuation",
                    help="secret key contains punctuation")
    _arg.add_argument(dest="key_length", type=int, nargs="?", metavar="DIGIT",
                      help="the length of secret key, default is random")


@CommandExecutor(add_cmd)
def run_cmd(cmds: Command) -> int:
    chr: str = cmds.args.characters  # pylint: disable=redefined-builtin
    if cmds.args.enable_digit:
        chr += string.digits
    if cmds.args.enable_letter:
        chr += string.ascii_letters
    if cmds.args.enable_lowercase:
        chr += string.ascii_lowercase
    if cmds.args.enable_uppercase:
        chr += string.ascii_uppercase
    if cmds.args.enable_punctuation:
        chr += string.punctuation
    len: Optional[int] = cmds.args.key_length  # pylint: disable=W0622
    key: Pass = Pass.random_generate(len, chr)
    cmds.stdout(key.value)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
