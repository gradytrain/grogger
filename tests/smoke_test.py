"""Smoke test for the grogger distributions.

Verifies that the built wheel and source distribution install correctly
and that the package imports and logs without error.
"""

import logging

from grogger import Grogger


def main() -> None:
    logger = Grogger(script_name="grogger-smoke-test", log_level=logging.INFO)
    logger.log("Grogger installed successfully")
    logger.stop_success()


if __name__ == "__main__":
    main()
