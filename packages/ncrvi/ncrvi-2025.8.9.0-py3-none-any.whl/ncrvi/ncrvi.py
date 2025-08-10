"""Determine the number of firmware components that report version info"""

import subprocess
import sys
import sysconfig
import argparse
import pytest
import os
from pathlib import PurePath
from typing import Optional

class Ncrvi:

    def __init__(self,
                 me: Optional[str] = PurePath(__file__).stem,
                 purpose : Optional[str] = __doc__) -> None:
        """Kick off scanning the command-line"""
        self.args = self.parse_cmd_line(me, purpose)

    def parse_cmd_line(self, me: str, purpose: str) -> Optional[argparse.Namespace]:
        """Read options, show help

        :param me: The name used to identify the program in the usage display
        :param purpose: Explain what the program does
        :returns: An (argparse) namespace holding the args
        """
        # Parse the command line
        try:
            parser = argparse.ArgumentParser(
                prog=me,
                description=purpose,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            parser.add_argument(
                '-w', '--initial-wait',
                type=float,
                default=1.0,
                help='''
                    number of seconds to wait before starting the tests
                    ''',
            )
            parser.add_argument(
                '-p', '--power-on-wait',
                type=float,
                default=5.0,
                help='''
                    number of seconds to wait before powering on the target
                    ''',
            )
            parser.add_argument(
                '-P', '--power-off-wait',
                type=float,
                default=0.0,
                help='''
                    number of seconds to wait before powering off the target
                    ''',
            )
            parser.add_argument(
                '-N', '--how-often',
                type=int,
                default=10,
                help='''
                    how often to run the show
                    ''',
            )
            parser.add_argument(
                '-s', '--settling-delay',
                type=int,
                default=2.0,
                help='''
                    how long to wait (in seconds) before reaching for the stars
                    ''',
            )
            parser.add_argument(
                '-e', '--expected-components',
                type=int,
                default=20,
                help='''
                    the success criterion
                    ''',
            )
            parser.add_argument(
                '-u', '--user',
                type=str,
                help='''
                    the user to book the target, etc.
                    ''',
            )
            parser.add_argument(
                'target',
                type=str,
                choices=['this', 'that'],
                help='''
                    the target to work on
                    ''',
            )
            return parser.parse_args()
        except argparse.ArgumentError as exc:
            raise ValueError('The command-line is indecipherable')

    def __call__(self) -> int:
        """Run the show

        :returns: Whatever pytest.main() does
        """
        os.environ['INITIAL_WAIT'] = str(self.args.initial_wait)
        os.environ['POWER_ON_WAIT'] = str(self.args.power_on_wait)
        os.environ['POWER_OFF_WAIT'] = str(self.args.power_off_wait)
        os.environ['HOW_OFTEN'] = str(self.args.how_often)
        os.environ['SETTLING_DELAY'] = str(self.args.settling_delay)
        os.environ['EXPECTED_COMPONENTS'] = str(self.args.expected_components)
        os.environ['USER'] = self.args.user or str()
        os.environ['TARGET'] = self.args.target or str()
        return pytest.main(['--verbose',
                           # Needs proper installation via pip...
                           PurePath(sysconfig.get_paths()["purelib"]) / PurePath(__file__).stem],)

def __main() -> int:

    N = Ncrvi()
    sys.exit(N())

def main() -> int:
    try:
        sys.exit(__main())
    except Exception:
        import traceback
        print(traceback.format_exc(), file=sys.stderr, end='')
        sys.exit(2)
    except KeyboardInterrupt:
        print('\rInterrupted by user', file=sys.stderr)
        sys.exit(3)

if __name__ == '__main__':
    sys.exit(main())
