"""The work time log app tracks working hours in an interaction model similar to git."""

import sys

from work.core import Color, InvalidOperationWarning, Work

### CLI entrypoint ###


def cli():
    """Command line interface entrypoint."""
    try:
        Work().main()
    except KeyboardInterrupt:
        print("Cancelled")
        sys.exit(130)
    # Invalid operations are considered part of the program flow and printed
    except InvalidOperationWarning as warning:
        print(warning)
        sys.exit(1)
    # Exceptions are handled depending on the mode
    except Exception as error:  # pylint: disable=broad-except
        # Debug mode: Raise
        if Work.debug:
            raise error

        # Normal mode: In case of an exception, print the message and exit.
        print(f"{Color.color('ERROR', Color.RED)}: {error}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
