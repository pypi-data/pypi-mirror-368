ncrvi
=====

Determine the number of components returning version information

Example usage
-------------

.. code-block:: bash

    $ ncrvi -h
    usage: ncrvi [-h] [-w INITIAL_WAIT] [-p POWER_ON_WAIT] [-P POWER_OFF_WAIT] [-N HOW_OFTEN] [-s SETTLING_DELAY] [-e EXPECTED_COMPONENTS] [-u USER] {this,that}

    Determine the number of firmware components that report version info

    positional arguments:
      {this,that}           the target to work on

    options:
      -h, --help            show this help message and exit
      -w, --initial-wait INITIAL_WAIT
                            number of seconds to wait before starting the tests (default: 1.0)
      -p, --power-on-wait POWER_ON_WAIT
                            number of seconds to wait before powering on the target (default: 5.0)
      -P, --power-off-wait POWER_OFF_WAIT
                            number of seconds to wait before powering off the target (default: 0.0)
      -N, --how-often HOW_OFTEN
                            how often to run the show (default: 10)
      -s, --settling-delay SETTLING_DELAY
                            how long to wait (in seconds) before reaching for the stars (default: 2.0)
      -e, --expected-components EXPECTED_COMPONENTS
                            the success criterion (default: 20)
      -u, --user USER       the user to book the target, etc. (default: None)

Installation
------------

The `project <https://pypi.org/project/ncrvi/>`_ is on PyPI, so simply run

.. code-block:: bash

    $ python -m pip install ncrvi
