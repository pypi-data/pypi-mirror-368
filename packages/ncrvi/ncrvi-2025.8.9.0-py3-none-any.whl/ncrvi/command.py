"""Simple wrapper for specifying and running a command"""

import subprocess
from typing import Optional

class CommandExecutionError(subprocess.CalledProcessError):

    def __init__(self, msg, returncode=42, cmd=str()):
        self.msg = msg
        self.returncode = returncode
        self.cmd = cmd
        subprocess.CalledProcessError(returncode=self.returncode, cmd=self.cmd)

    def __str__(self):
        return f'{self.msg}'

class Command:

    def __init__(self, *pargs):
        self.pargs = pargs;

    def __call__(self) -> Optional[str]:
        """Execute the command

        :returns: The command's output
        """
        cmd_and_args = [it for it in self.pargs]

        try:
            with subprocess.Popen(cmd_and_args, stdout=subprocess.PIPE) as p:
                outs, errs = p.communicate()
            assert p.returncode == 0
        except (AssertionError, subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise CommandExecutionError(f'the command "{cmd_and_args!r}" was unhappy') from exc

        return outs.decode().rstrip()
