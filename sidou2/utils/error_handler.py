# Import necessary modules
import sqlite3  # For interacting with SQLite databases
import logging  # For logging errors and other information
import traceback  # For getting detailed traceback information during errors
import sys  # For system-specific parameters and functions (not explicitly used here but often useful in error handlers)
import os  # For interacting with the operating system, like creating directories or paths

# --- Logging Configuration ---
# Define the directory for log files. It will be a 'logs' folder in the parent directory of this file's location.
log_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
# Create the 'logs' directory if it doesn't already exist.
os.makedirs(log_dir, exist_ok=True)
# Define the full path for the error log file.
log_file = os.path.join(log_dir, "app_errors.log")

# Basic logging setup:
# - Set the minimum logging level to ERROR (only ERROR and CRITICAL messages will be processed).
# - Define the format for log messages, including timestamp, logger name, log level, and the message.
# - Specify handlers:
#   - FileHandler: Writes log messages to the 'app_errors.log' file.
#   - StreamHandler: Prints log messages to the console.
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Corrected 'sasctime' to 'asctime'
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

# Get a logger instance with a specific name for this application module.
# This helps in identifying the source of log messages.
logger = logging.getLogger("inventory_app")


# --- Custom Exception Classes ---
class DatabaseError(Exception):
    """Custom exception to be raised for database-related errors.
    This allows for more specific error handling than generic Exception.
    """

    pass


class ValidationError(Exception):
    """Custom exception to be raised for data validation errors.
    This helps distinguish validation issues from other types of errors.
    """

    pass


# --- Decorator for Database Error Handling ---
def handle_db_error(func):
    """
    A decorator function designed to wrap other functions that perform database operations.
    It provides a centralized way to catch and handle common SQLite errors,
    translating them into more user-friendly `DatabaseError` exceptions.
    """

    def wrapper(*args, **kwargs):
        """
        The inner function that replaces the decorated function.
        It executes the original function within a try-except block.
        """
        try:
            # Attempt to execute the original (decorated) function
            return func(*args, **kwargs)
        except sqlite3.IntegrityError as e:
            # Handle SQLite integrity errors (e.g., UNIQUE constraint violations, FOREIGN KEY constraint failures).
            error_msg = f"Database integrity error: {str(e)}"
            logger.error(f"{error_msg} in {func.__name__}")  # Log the detailed error.
            # Provide more specific user-friendly messages based on the error content.
            if "UNIQUE constraint failed" in str(e):
                raise DatabaseError("Cette entrée existe déjà dans la base de données.")
            elif "FOREIGN KEY constraint failed" in str(e):
                raise DatabaseError(
                    "Impossible de supprimer cet élément car il est référencé ailleurs."
                )
            elif "CHECK constraint failed" in str(e):
                raise DatabaseError(
                    "Les valeurs entrées ne respectent pas les contraintes de la base de données."
                )
            else:
                # For other integrity errors, raise a more generic message.
                raise DatabaseError(
                    f"Erreur d'intégrité de la base de données: {str(e)}"
                )
        except sqlite3.Error as e:
            # Handle other SQLite errors (e.g., connection issues, syntax errors).
            error_msg = f"Database error: {str(e)}"
            logger.error(f"{error_msg} in {func.__name__}")  # Log the detailed error.
            raise DatabaseError(f"Erreur de base de données: {str(e)}")
        except Exception as e:
            # Handle any other unexpected exceptions.
            error_msg = f"Unexpected error: {str(e)}"
            # Log the error along with a full stack trace for debugging.
            logger.error(f"{error_msg} in {func.__name__}\n{traceback.format_exc()}")
            raise  # Re-raise the original exception.

    return wrapper


# --- Utility Function for Logging Errors ---
def log_error(e, context=""):
    """
    A utility function to log an error with additional context.
    This can be used for logging errors that are not caught by the `handle_db_error` decorator.

    Args:
        e (Exception): The exception object that was caught.
        context (str, optional): A string providing context about where the error occurred.
                                Defaults to an empty string.

    Returns:
        str: A formatted error message string (error type and message).
    """
    error_type = type(e).__name__  # Get the type of the exception (e.g., "ValueError").
    error_msg = str(e)  # Get the string representation of the exception message.
    stack_trace = traceback.format_exc()  # Get the full stack trace.

    # Log the error with context, type, message, and stack trace.
    logger.error(f"{context} - {error_type}: {error_msg}\n{stack_trace}")

    # Return a simple error message string.
    return f"{error_type}: {error_msg}"
