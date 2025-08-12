# conftest.py
import pytest
import logging

def pytest_configure(config):
    """
    Configure logging for pytest.

    This hook is called once at the beginning of a test run.
    It sets up the basic logging configuration for the root logger,
    directing log messages to the console (standard error by default).
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Set the logging level (e.g., INFO, DEBUG, WARNING, ERROR, CRITICAL)
    # INFO is a good balance for seeing important messages during tests.
    root_logger.setLevel(logging.INFO)

    # Define a logging format
    # The format includes:
    # - %(asctime)s: Current time when the log record was created
    # - %(levelname)s: Text logging level for the current message (e.g., INFO)
    # - %(name)s: Name of the logger (e.g., 'root' or a specific module name)
    # - %(filename)s: Filename where the logging call was made
    # - %(lineno)d: Line number in the file where the logging call was made
    # - %(message)s: The actual log message
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # Check if a console handler already exists to avoid duplicate messages
    if not any(isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers):
        # Create a StreamHandler to output log messages to the console
        console_handler = logging.StreamHandler()
        # Set the formatter for the console handler
        console_handler.setFormatter(formatter)
        # Add the console handler to the root logger
        root_logger.addHandler(console_handler)

    # Optionally, you can disable the default pytest log capturing if you
    # want to fully control logging via this conftest.py.
    # If not disabled, pytest might still capture logs and present them differently.
    # config.option.log_cli = False
    # config.option.log_cli_level = "INFO"
    # config.option.log_cli_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    # config.option.log_cli_date_format = "%H:%M:%S"

    # You can also set specific logger levels for third-party libraries if they are too noisy
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    # logging.getLogger("Faker").setLevel(logging.WARNING)

